// Benchmark for the CPU-side per-frame waveform vertex rebuild.
//
// The dominant per-frame cost of the allshader waveform path on the QWidget
// (rendergraph_gl) backend is the scalar CPU vertex-buffer rebuild done every
// vsync in `allshader::WaveformRenderer{RGB,Filtered}::preprocess()` ->
// `preprocessInner()`. That loop walks the whole visible waveform range,
// reduces per-pixel min/max over the WaveformData, and rewrites the entire
// client-side vertex buffer (no VBOs -- the P-22 / AP-12 target). This bench
// drives that exact path over a scripted scrubbing scene and reports the
// per-frame time distribution (p50 / p90 / p99 / max), the input to EVD-0001.
//
// This is a pure-CPU measurement: `preprocess()` touches only client-side
// geometry memory and never a GL context, so no offscreen surface is needed
// (Phase A of the baseline dossier). It lives entirely in the test/bench tree
// and does not touch the RT audio path.
//
// Run: build/mixxx-test --benchmark --benchmark_filter=BM_Waveform

#include <benchmark/benchmark.h>

#ifdef __APPLE__
#ifndef GL_SILENCE_DEPRECATION
#define GL_SILENCE_DEPRECATION
#endif
#include <OpenGL/OpenGL.h> // CGL: a headless GL context, no window server / QPA
#include <OpenGL/gl.h>     // legacy-profile core GL (glGenBuffers/glBufferData…)
#endif

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <vector>

#include "rendergraph/geometry.h"
#include "track/track.h"
#include "waveform/renderers/allshader/waveformrendererfiltered.h"
#include "waveform/renderers/allshader/waveformrendererrgb.h"
#include "waveform/renderers/waveformrendererabstract.h"
#include "waveform/renderers/waveformwidgetrenderer.h"
#include "waveform/waveform.h"

namespace {

// A realistic full-window deck waveform on a Retina display.
constexpr int kWidth = 1920;
constexpr int kHeight = 200;
constexpr float kDevicePixelRatio = 2.0f;

// Synthetic track: 5 minutes at 44.1 kHz, analysed at a typical 441 Hz visual
// sample rate -> ~264k WaveformData points, matching a real analysed waveform.
constexpr int kAudioSampleRate = 44100;
constexpr int kDurationSeconds = 300;
constexpr int kVisualSampleRate = 441;

// Default zoom expressed as visual frames per device pixel (WaveformWidget
// factory default zoom is 3.0).
constexpr double kVisualFramesPerPixel = 3.0;

// Number of distinct scrubbing positions swept across the track. Each bench
// iteration renders one frame at the next position, cycling through these.
constexpr int kScrubSteps = 512;

// Exposes the per-frame displayed window that onPreRender() would normally
// compute from the engine's VisualPlayPosition, so the bench can drive the
// renderer's preprocess() without the full ControlObject / VSync plumbing.
class BenchWaveformWidgetRenderer : public WaveformWidgetRenderer {
  public:
    BenchWaveformWidgetRenderer() = default;

    void setDisplayWindow(double first, double last) {
        m_firstDisplayedPosition[::WaveformRendererAbstract::Play] = first;
        m_lastDisplayedPosition[::WaveformRendererAbstract::Play] = last;
        m_firstDisplayedPosition[::WaveformRendererAbstract::Slip] = first;
        m_lastDisplayedPosition[::WaveformRendererAbstract::Slip] = last;
    }
};

WaveformPointer makeSyntheticWaveform() {
    const auto frameLength =
            static_cast<SINT>(kAudioSampleRate) * kDurationSeconds;
    auto pWaveform = WaveformPointer(new Waveform(
            kAudioSampleRate, frameLength, kVisualSampleRate, -1, 0));

    // Fill with deterministic pseudo-random band energies so the per-pixel
    // min/max reduction does real work (a flat buffer would be unrealistic).
    const int dataSize = pWaveform->getDataSize();
    WaveformData* pData = pWaveform->data();
    uint32_t lcg = 0x1234567u;
    for (int i = 0; i < dataSize; ++i) {
        lcg = lcg * 1664525u + 1013904223u;
        WaveformData& d = pData[i];
        d.filtered.low = static_cast<unsigned char>((lcg >> 8) & 0xFF);
        d.filtered.mid = static_cast<unsigned char>((lcg >> 16) & 0xFF);
        d.filtered.high = static_cast<unsigned char>((lcg >> 24) & 0xFF);
        d.filtered.all = static_cast<unsigned char>(lcg & 0xFF);
    }
    pWaveform->setCompletion(dataSize);
    return pWaveform;
}

TrackPointer makeSyntheticTrack(const WaveformPointer& pWaveform) {
    TrackPointer pTrack = Track::newDummy(QStringLiteral("/bench.wav"), TrackId());
    pTrack->setWaveform(pWaveform);
    return pTrack;
}

// The normalized track fraction visible in one frame at the target zoom.
double displayWindow(int dataSize) {
    const double pixelLength = static_cast<double>(kWidth) * kDevicePixelRatio;
    const double visualFramesSize = static_cast<double>(dataSize) / 2.0;
    const double window = kVisualFramesPerPixel * pixelLength / visualFramesSize;
    return std::min(window, 1.0);
}

// Drives `renderer.preprocess()` once per bench iteration at a scrubbing
// position, times each call, and reports the frame-time distribution.
template<typename Renderer>
void runScrub(benchmark::State& state,
        BenchWaveformWidgetRenderer& wwr,
        Renderer& renderer,
        double window) {
    const double pMin = window / 2.0;
    const double pMax = 1.0 - window / 2.0;
    const double span = std::max(pMax - pMin, 0.0);

    std::vector<double> frameUs;
    frameUs.reserve(1 << 16);

    std::size_t frame = 0;
    for (auto _ : state) {
        const double t = (kScrubSteps > 1)
                ? static_cast<double>(frame % kScrubSteps) / (kScrubSteps - 1)
                : 0.0;
        const double p = pMin + span * t;
        wwr.setDisplayWindow(p - window / 2.0, p + window / 2.0);

        const auto start = std::chrono::steady_clock::now();
        renderer.preprocess();
        const auto end = std::chrono::steady_clock::now();

        // Prevent the whole rebuild from being optimized away.
        benchmark::DoNotOptimize(renderer.geometry().vertexCount());

        frameUs.push_back(
                std::chrono::duration<double, std::micro>(end - start).count());
        ++frame;
    }

    if (frameUs.empty()) {
        return;
    }

    std::sort(frameUs.begin(), frameUs.end());
    const auto pct = [&](double q) {
        const auto idx = static_cast<std::size_t>(
                q * static_cast<double>(frameUs.size() - 1) + 0.5);
        return frameUs[idx];
    };
    double sum = 0.0;
    for (double v : frameUs) {
        sum += v;
    }

    const double p50 = pct(0.50);
    const double p90 = pct(0.90);
    const double p99 = pct(0.99);
    const double maxv = frameUs.back();
    const double minv = frameUs.front();
    const double mean = sum / static_cast<double>(frameUs.size());

    // Counters (microseconds). Reported per benchmark row.
    state.counters["p50_us"] = p50;
    state.counters["p90_us"] = p90;
    state.counters["p99_us"] = p99;
    state.counters["max_us"] = maxv;
    state.counters["min_us"] = minv;
    state.counters["mean_us"] = mean;
    state.counters["frames"] = static_cast<double>(frameUs.size());

    // Authoritative human-readable summary (not subject to counter averaging).
    char label[256];
    std::snprintf(label,
            sizeof(label),
            "p50=%.1fus p90=%.1fus p99=%.1fus max=%.1fus min=%.1fus n=%zu",
            p50,
            p90,
            p99,
            maxv,
            minv,
            frameUs.size());
    state.SetLabel(label);
    state.SetItemsProcessed(static_cast<int64_t>(frameUs.size()));
}

void BM_WaveformRGBPreprocess(benchmark::State& state) {
    WaveformPointer pWaveform = makeSyntheticWaveform();
    TrackPointer pTrack = makeSyntheticTrack(pWaveform);

    BenchWaveformWidgetRenderer wwr;
    wwr.setTrack(pTrack);
    wwr.resizeRenderer(kWidth, kHeight, kDevicePixelRatio);

    allshader::WaveformRendererRGB renderer(&wwr,
            ::WaveformRendererAbstract::Play,
            ::WaveformRendererSignalBase::Option::None);

    runScrub(state, wwr, renderer, displayWindow(pWaveform->getDataSize()));
}

void BM_WaveformFilteredPreprocess(benchmark::State& state) {
    WaveformPointer pWaveform = makeSyntheticWaveform();
    TrackPointer pTrack = makeSyntheticTrack(pWaveform);

    BenchWaveformWidgetRenderer wwr;
    wwr.setTrack(pTrack);
    wwr.resizeRenderer(kWidth, kHeight, kDevicePixelRatio);

    allshader::WaveformRendererFiltered renderer(&wwr,
            /*rgbStacked=*/false,
            ::WaveformRendererSignalBase::Option::None);

    runScrub(state, wwr, renderer, displayWindow(pWaveform->getDataSize()));
}

#ifdef __APPLE__
// A headless OpenGL context via CGL (Core OpenGL). Qt's offscreen QPA yields no
// GL context in the CLI test binary (that is why the GL benches historically
// skipped), but CGL creates a real context with no window-server surface, so
// the upload / combined-scrub benches run headless. Prefers a hardware context;
// falls back to software so the bench still produces a number if no accelerated
// headless GPU is available (flagged in the EVD when that happens).
class HeadlessGLContext {
  public:
    HeadlessGLContext() {
        const CGLPixelFormatAttribute accel[] = {
                kCGLPFAAccelerated,
                kCGLPFAOpenGLProfile,
                static_cast<CGLPixelFormatAttribute>(kCGLOGLPVersion_Legacy),
                static_cast<CGLPixelFormatAttribute>(0)};
        const CGLPixelFormatAttribute software[] = {
                kCGLPFAOpenGLProfile,
                static_cast<CGLPixelFormatAttribute>(kCGLOGLPVersion_Legacy),
                static_cast<CGLPixelFormatAttribute>(0)};
        CGLPixelFormatObj pix = nullptr;
        GLint npix = 0;
        if (CGLChoosePixelFormat(accel, &pix, &npix) != kCGLNoError ||
                pix == nullptr) {
            if (CGLChoosePixelFormat(software, &pix, &npix) != kCGLNoError ||
                    pix == nullptr) {
                return;
            }
        }
        if (CGLCreateContext(pix, nullptr, &m_ctx) != kCGLNoError) {
            m_ctx = nullptr;
        }
        CGLDestroyPixelFormat(pix);
        if (m_ctx != nullptr) {
            CGLSetCurrentContext(m_ctx);
            // Report which GL renderer we bound so the EVD can flag whether the
            // upload numbers are hardware (representative) or a software fallback.
            const GLubyte* renderer = glGetString(GL_RENDERER);
            const GLubyte* version = glGetString(GL_VERSION);
            std::fprintf(stderr,
                    "[HeadlessGLContext] renderer=%s version=%s\n",
                    renderer ? reinterpret_cast<const char*>(renderer) : "?",
                    version ? reinterpret_cast<const char*>(version) : "?");
        }
    }
    ~HeadlessGLContext() {
        if (m_ctx != nullptr) {
            CGLSetCurrentContext(nullptr);
            CGLDestroyContext(m_ctx);
        }
    }
    HeadlessGLContext(const HeadlessGLContext&) = delete;
    HeadlessGLContext& operator=(const HeadlessGLContext&) = delete;
    bool valid() const {
        return m_ctx != nullptr;
    }

  private:
    CGLContextObj m_ctx = nullptr;
};
#endif // __APPLE__

// -----------------------------------------------------------------------------
// GPU upload cost of the per-frame vertex buffer (the P-22 / AP-12 win).
//
// The persistent-VBO change in
// src/rendergraph/opengl/backend/basegeometrynode.cpp replaces a per-draw
// client-memory bind (setAttributeArray) -- which forced the driver to copy the
// *whole* vertex buffer CPU->GPU on every glDrawArrays -- with a GL buffer
// object that is re-uploaded only when the geometry is marked dirty. Whenever
// the waveform does not change between frames (a paused deck, a static display
// window -- the common idle case that still redraws every vsync), the new path
// performs ZERO upload and draws straight from GPU memory.
//
// This bench quantifies the copy that is eliminated in that case: it times a
// single full upload of a waveform-sized RGB vertex buffer (glBufferData orphan
// + glBufferSubData) into a real GL buffer, with glFinish() to force the
// transfer to complete. That per-frame cost is exactly what the VBO path saves
// for every unchanged frame.
//
// Needs a live GL context, so unlike the pure-CPU benches above it opens an
// offscreen surface. If no context can be created in this environment the bench
// skips honestly rather than fabricating a number.
//
// Run: build/mixxx-test --benchmark --benchmark_filter=BM_WaveformVboUpload

// Bytes of one RGB waveform frame's vertex buffer at the bench scene:
// 6 vertices per line (2 triangles) * (pixelLength + 1) lines, each vertex an
// RGBColoredPoint2D = 2 (pos) + 3 (color) floats = 20 bytes. This matches the
// geometry the RGB renderer allocates in preprocessInner().
constexpr int kVertexBytes = 5 * static_cast<int>(sizeof(float));
int rgbFrameByteSize() {
    const int pixelLength = static_cast<int>(kWidth * kDevicePixelRatio);
    const int vertices = 6 * (pixelLength + 1);
    return vertices * kVertexBytes;
}

void BM_WaveformVboUpload(benchmark::State& state) {
    HeadlessGLContext glctx;
    if (!glctx.valid()) {
        state.SkipWithError(
                "headless CGL context unavailable -- upload delta needs a GL "
                "context");
        return;
    }

    const int byteSize = rgbFrameByteSize();
    std::vector<float> src(byteSize / sizeof(float));
    uint32_t lcg = 0x9e3779b9u;
    for (auto& v : src) {
        lcg = lcg * 1664525u + 1013904223u;
        v = static_cast<float>(lcg & 0xFFFF) / 65535.0f;
    }

    GLuint vbo = 0;
    glGenBuffers(1, &vbo);
    glBindBuffer(GL_ARRAY_BUFFER, vbo);
    glBufferData(GL_ARRAY_BUFFER, byteSize, src.data(), GL_DYNAMIC_DRAW);
    glFinish();

    std::vector<double> frameUs;
    frameUs.reserve(1 << 16);

    for (auto _ : state) {
        const auto start = std::chrono::steady_clock::now();
        // One per-frame upload: orphan the previous storage then refill --
        // exactly what render() does when the geometry is dirty, and exactly
        // what it now SKIPS when the geometry is unchanged. glBufferSubData
        // must copy the client data into driver storage before it returns, so
        // this times the CPU-side, render-thread cost of the upload (the copy
        // eliminated for every unchanged frame). No glFinish() here: we measure
        // render-thread occupancy, not full GPU-completion latency.
        glBufferData(GL_ARRAY_BUFFER, byteSize, nullptr, GL_DYNAMIC_DRAW);
        glBufferSubData(GL_ARRAY_BUFFER, 0, byteSize, src.data());
        const auto end = std::chrono::steady_clock::now();
        frameUs.push_back(
                std::chrono::duration<double, std::micro>(end - start).count());
    }

    glFinish();
    glDeleteBuffers(1, &vbo);

    if (frameUs.empty()) {
        return;
    }
    std::sort(frameUs.begin(), frameUs.end());
    const auto pct = [&](double q) {
        const auto idx = static_cast<std::size_t>(
                q * static_cast<double>(frameUs.size() - 1) + 0.5);
        return frameUs[idx];
    };
    double sum = 0.0;
    for (double v : frameUs) {
        sum += v;
    }
    const double p50 = pct(0.50);
    const double p90 = pct(0.90);
    const double p99 = pct(0.99);
    const double maxv = frameUs.back();
    const double minv = frameUs.front();
    const double mean = sum / static_cast<double>(frameUs.size());

    state.counters["bytes"] = static_cast<double>(byteSize);
    state.counters["p50_us"] = p50;
    state.counters["p90_us"] = p90;
    state.counters["p99_us"] = p99;
    state.counters["max_us"] = maxv;
    state.counters["min_us"] = minv;
    state.counters["mean_us"] = mean;

    char label[256];
    std::snprintf(label,
            sizeof(label),
            "upload=%dB p50=%.2fus p90=%.2fus p99=%.2fus max=%.2fus min=%.2fus n=%zu",
            byteSize,
            p50,
            p90,
            p99,
            maxv,
            minv,
            frameUs.size());
    state.SetLabel(label);
    state.SetItemsProcessed(static_cast<int64_t>(frameUs.size()));
}

// -----------------------------------------------------------------------------
// Combined per-frame cost of ACTIVE SCRUBBING -- the coverage gap (EVD-0003).
//
// The benches above measure the two halves in isolation: the CPU vertex rebuild
// (BM_WaveformRGBPreprocess, no GL) and a fixed-size GPU upload
// (BM_WaveformVboUpload, decoupled from scrub position). Neither measures what a
// scrubbing frame actually pays: when the display window moves every frame,
// preprocess() rebuilds the whole client vertex buffer AND marks the geometry
// dirty, which forces the mandatory persistent-VBO re-upload for that *same*
// frame. This bench drives that combined frame -- preprocess() then the exact
// dirty re-upload src/rendergraph/opengl/backend/basegeometrynode.cpp performs
// (glBufferData orphan + glBufferSubData of geometry.vertexData()) -- against a
// live offscreen GL context, sweeping scrub positions, reporting the combined
// per-frame distribution. This is precisely the regime the persistent-VBO win
// does NOT help (every frame is dirty), and the baseline the scrub-regime
// optimization (PS-MTL-03) is judged against.
//
// Needs a live GL context; skips honestly if none is available.
//
// Run: build/mixxx-test --benchmark --benchmark_filter=BM_WaveformScrubFrame

void BM_WaveformScrubFrame(benchmark::State& state) {
    HeadlessGLContext glctx;
    if (!glctx.valid()) {
        state.SkipWithError(
                "headless CGL context unavailable -- combined scrub-frame needs "
                "a GL context");
        return;
    }

    WaveformPointer pWaveform = makeSyntheticWaveform();
    TrackPointer pTrack = makeSyntheticTrack(pWaveform);

    BenchWaveformWidgetRenderer wwr;
    wwr.setTrack(pTrack);
    wwr.resizeRenderer(kWidth, kHeight, kDevicePixelRatio);

    allshader::WaveformRendererRGB renderer(&wwr,
            ::WaveformRendererAbstract::Play,
            ::WaveformRendererSignalBase::Option::None);

    const double window = displayWindow(pWaveform->getDataSize());
    const double pMin = window / 2.0;
    const double pMax = 1.0 - window / 2.0;
    const double span = std::max(pMax - pMin, 0.0);

    GLuint vbo = 0;
    glGenBuffers(1, &vbo);
    glBindBuffer(GL_ARRAY_BUFFER, vbo);
    int vboByteSize = -1;

    std::vector<double> frameUs;
    frameUs.reserve(1 << 16);

    std::size_t frame = 0;
    for (auto _ : state) {
        const double t = (kScrubSteps > 1)
                ? static_cast<double>(frame % kScrubSteps) / (kScrubSteps - 1)
                : 0.0;
        const double p = pMin + span * t;
        wwr.setDisplayWindow(p - window / 2.0, p + window / 2.0);

        const auto start = std::chrono::steady_clock::now();
        // 1. CPU vertex rebuild for the new window (marks geometry dirty).
        renderer.preprocess();
        // 2. The mandatory dirty re-upload for this frame -- the exact path
        //    basegeometrynode.cpp takes when the geometry is dirty. Every
        //    scrubbing frame is dirty, so this always runs (the VBO win, which
        //    skips the upload for unchanged frames, does not apply here).
        auto& geometry = renderer.geometry();
        const int vertexBytes =
                geometry.vertexCount() * geometry.sizeOfVertex();
        if (vertexBytes != vboByteSize) {
            glBufferData(GL_ARRAY_BUFFER,
                    vertexBytes,
                    geometry.vertexData(),
                    GL_DYNAMIC_DRAW);
            vboByteSize = vertexBytes;
        } else {
            glBufferData(
                    GL_ARRAY_BUFFER, vertexBytes, nullptr, GL_DYNAMIC_DRAW);
            glBufferSubData(
                    GL_ARRAY_BUFFER, 0, vertexBytes, geometry.vertexData());
        }
        const auto end = std::chrono::steady_clock::now();

        benchmark::DoNotOptimize(geometry.vertexCount());
        frameUs.push_back(
                std::chrono::duration<double, std::micro>(end - start).count());
        ++frame;
    }

    glFinish();
    glDeleteBuffers(1, &vbo);

    if (frameUs.empty()) {
        return;
    }
    std::sort(frameUs.begin(), frameUs.end());
    const auto pct = [&](double q) {
        const auto idx = static_cast<std::size_t>(
                q * static_cast<double>(frameUs.size() - 1) + 0.5);
        return frameUs[idx];
    };
    double sum = 0.0;
    for (double v : frameUs) {
        sum += v;
    }
    const double p50 = pct(0.50);
    const double p90 = pct(0.90);
    const double p99 = pct(0.99);
    const double maxv = frameUs.back();
    const double minv = frameUs.front();
    const double mean = sum / static_cast<double>(frameUs.size());

    state.counters["p50_us"] = p50;
    state.counters["p90_us"] = p90;
    state.counters["p99_us"] = p99;
    state.counters["max_us"] = maxv;
    state.counters["min_us"] = minv;
    state.counters["mean_us"] = mean;
    state.counters["frames"] = static_cast<double>(frameUs.size());

    char label[256];
    std::snprintf(label,
            sizeof(label),
            "p50=%.1fus p90=%.1fus p99=%.1fus max=%.1fus min=%.1fus n=%zu",
            p50,
            p90,
            p99,
            maxv,
            minv,
            frameUs.size());
    state.SetLabel(label);
    state.SetItemsProcessed(static_cast<int64_t>(frameUs.size()));
}

} // namespace

// Fixed iteration count so two runs are directly comparable (reproducibility
// gate) and the percentile sample size is stable.
BENCHMARK(BM_WaveformRGBPreprocess)
        ->Iterations(4000)
        ->Unit(benchmark::kMicrosecond)
        ->UseRealTime();
BENCHMARK(BM_WaveformFilteredPreprocess)
        ->Iterations(4000)
        ->Unit(benchmark::kMicrosecond)
        ->UseRealTime();
BENCHMARK(BM_WaveformVboUpload)
        ->Iterations(4000)
        ->Unit(benchmark::kMicrosecond)
        ->UseRealTime();
BENCHMARK(BM_WaveformScrubFrame)
        ->Iterations(4000)
        ->Unit(benchmark::kMicrosecond)
        ->UseRealTime();
