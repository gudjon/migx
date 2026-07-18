// Headless pixel ground-truth for the waveform render (the "GUI eyeball", solved).
//
// The VBO win and the Wave-2a idle-frame skip both had one gate not reachable in
// the CLI: does the geometry actually render to CORRECT PIXELS, and does a paused
// deck render identically frame-to-frame? This renders the allshader RGB waveform
// through a real GL pipeline on a headless CGL context (Apple M4, no window
// server), reads the framebuffer back, writes PNGs a human/agent can inspect, and
// asserts the ground truth:
//   - the waveform is actually drawn (not a blank frame);
//   - a paused frame (idle-skip) is PIXEL-identical on redraw;
//   - a moved playhead renders a DIFFERENT image.
// This converts the subjective "eyeball" into objective evidence (DC-PDUX-5.1 /
// 5.4 / 5.6): verify real rendered output, not a proxy.

#include <gtest/gtest.h>

#ifdef __APPLE__
#ifndef GL_SILENCE_DEPRECATION
#define GL_SILENCE_DEPRECATION
#endif
#include <OpenGL/OpenGL.h>
#include <OpenGL/gl.h>
#include <OpenGL/glext.h>
#endif

#include <QColor>
#include <QDir>
#include <QImage>
#include <QString>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <vector>

#include "rendergraph/geometry.h"
#include "track/track.h"
#include "waveform/renderers/allshader/waveformrendererrgb.h"
#include "waveform/renderers/waveformrendererabstract.h"
#include "waveform/renderers/waveformwidgetrenderer.h"
#include "waveform/waveform.h"

namespace {

using namespace rendergraph;

constexpr int kW = 960;
constexpr int kH = 160;

class TestWwr : public WaveformWidgetRenderer {
  public:
    void setWindow(double first, double last) {
        m_firstDisplayedPosition[::WaveformRendererAbstract::Play] = first;
        m_lastDisplayedPosition[::WaveformRendererAbstract::Play] = last;
        m_firstDisplayedPosition[::WaveformRendererAbstract::Slip] = first;
        m_lastDisplayedPosition[::WaveformRendererAbstract::Slip] = last;
    }
};

WaveformPointer makeWaveform() {
    constexpr int sampleRate = 44100;
    const auto frameLength = static_cast<SINT>(sampleRate) * 60;
    auto wf = WaveformPointer(new Waveform(sampleRate, frameLength, 441, -1, 0));
    const int n = wf->getDataSize();
    WaveformData* d = wf->data();
    uint32_t lcg = 0x1234567u;
    for (int i = 0; i < n; ++i) {
        lcg = lcg * 1664525u + 1013904223u;
        // A slow envelope so the rendered waveform has visible structure.
        const double env = 0.35 + 0.65 * (0.5 + 0.5 * std::sin(i * 0.0007));
        d[i].filtered.low = static_cast<unsigned char>(((lcg >> 8) & 0xFF) * env);
        d[i].filtered.mid = static_cast<unsigned char>(((lcg >> 16) & 0xFF) * env);
        d[i].filtered.high = static_cast<unsigned char>(((lcg >> 24) & 0xFF) * env);
        d[i].filtered.all = static_cast<unsigned char>((lcg & 0xFF) * env);
    }
    wf->setCompletion(n);
    return wf;
}

#ifdef __APPLE__
CGLContextObj makeContext() {
    const CGLPixelFormatAttribute attribs[] = {
            kCGLPFAAccelerated,
            kCGLPFAOpenGLProfile,
            static_cast<CGLPixelFormatAttribute>(kCGLOGLPVersion_Legacy),
            static_cast<CGLPixelFormatAttribute>(0)};
    CGLPixelFormatObj pix = nullptr;
    GLint npix = 0;
    if (CGLChoosePixelFormat(attribs, &pix, &npix) != kCGLNoError || !pix) {
        return nullptr;
    }
    CGLContextObj ctx = nullptr;
    CGLCreateContext(pix, nullptr, &ctx);
    CGLDestroyPixelFormat(pix);
    if (ctx) {
        CGLSetCurrentContext(ctx);
    }
    return ctx;
}

GLuint compileShader(GLenum type, const char* src) {
    GLuint s = glCreateShader(type);
    glShaderSource(s, 1, &src, nullptr);
    glCompileShader(s);
    GLint ok = 0;
    glGetShaderiv(s, GL_COMPILE_STATUS, &ok);
    if (!ok) {
        char log[512];
        glGetShaderInfoLog(s, sizeof(log), nullptr, log);
        std::fprintf(stderr, "[pixel-test] shader compile failed: %s\n", log);
    }
    return s;
}

// Renders the renderer's current geometry to a kW x kH RGBA image (top-left
// origin). Returns empty on GL setup failure.
QImage renderToImage(allshader::WaveformRendererRGB& renderer, double length, double breadth) {
    static const char* kVert =
            "#version 120\n"
            "attribute vec2 aPos;\n"
            "attribute vec3 aColor;\n"
            "uniform mat4 uMVP;\n"
            "varying vec3 vColor;\n"
            "void main(){ gl_Position = uMVP * vec4(aPos,0.0,1.0); vColor = aColor; }\n";
    static const char* kFrag =
            "#version 120\n"
            "varying vec3 vColor;\n"
            "void main(){ gl_FragColor = vec4(vColor,1.0); }\n";

    GLuint prog = glCreateProgram();
    glAttachShader(prog, compileShader(GL_VERTEX_SHADER, kVert));
    glAttachShader(prog, compileShader(GL_FRAGMENT_SHADER, kFrag));
    glBindAttribLocation(prog, 0, "aPos");
    glBindAttribLocation(prog, 1, "aColor");
    glLinkProgram(prog);

    GLuint tex = 0;
    glGenTextures(1, &tex);
    glBindTexture(GL_TEXTURE_2D, tex);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, kW, kH, 0, GL_RGBA, GL_UNSIGNED_BYTE, nullptr);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);

    GLuint fbo = 0;
    glGenFramebuffers(1, &fbo);
    glBindFramebuffer(GL_FRAMEBUFFER, fbo);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, tex, 0);
    if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE) {
        std::fprintf(stderr, "[pixel-test] FBO incomplete\n");
        return QImage();
    }

    const Geometry& g = renderer.geometry();
    GLuint vbo = 0;
    glGenBuffers(1, &vbo);
    glBindBuffer(GL_ARRAY_BUFFER, vbo);
    glBufferData(GL_ARRAY_BUFFER,
            g.vertexCount() * g.sizeOfVertex(),
            g.vertexData(),
            GL_STATIC_DRAW);

    glViewport(0, 0, kW, kH);
    glClearColor(0.08f, 0.08f, 0.09f, 1.0f);
    glClear(GL_COLOR_BUFFER_BIT);
    glUseProgram(prog);
    // Column-major ortho: [0,length]x[0,breadth] -> NDC [-1,1].
    const float mvp[16] = {
            2.0f / static_cast<float>(length), 0, 0, 0,
            0, 2.0f / static_cast<float>(breadth), 0, 0,
            0, 0, 1, 0,
            -1, -1, 0, 1};
    glUniformMatrix4fv(glGetUniformLocation(prog, "uMVP"), 1, GL_FALSE, mvp);
    const int stride = g.sizeOfVertex();
    glEnableVertexAttribArray(0);
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, stride, reinterpret_cast<void*>(0));
    glEnableVertexAttribArray(1);
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, reinterpret_cast<void*>(2 * sizeof(float)));
    glDrawArrays(GL_TRIANGLES, 0, g.vertexCount());
    glFinish();

    std::vector<uint8_t> px(static_cast<std::size_t>(kW) * kH * 4);
    glReadPixels(0, 0, kW, kH, GL_RGBA, GL_UNSIGNED_BYTE, px.data());

    glDeleteBuffers(1, &vbo);
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
    glDeleteFramebuffers(1, &fbo);
    glDeleteTextures(1, &tex);
    glDeleteProgram(prog);

    // GL origin is bottom-left; QImage is top-left -> flip vertically.
    QImage img(px.data(), kW, kH, QImage::Format_RGBA8888);
    return img.copy().mirrored(false, true);
}

// Fraction of pixels that are not the background clear color.
double drawnFraction(const QImage& img) {
    if (img.isNull()) {
        return 0.0;
    }
    long drawn = 0;
    const long total = static_cast<long>(img.width()) * img.height();
    for (int y = 0; y < img.height(); ++y) {
        for (int x = 0; x < img.width(); ++x) {
            const QRgb p = img.pixel(x, y);
            if (qRed(p) > 30 || qGreen(p) > 30 || qBlue(p) > 40) {
                if (!(qRed(p) < 30 && qGreen(p) < 30 && qBlue(p) < 40)) {
                    ++drawn;
                }
            }
        }
    }
    return static_cast<double>(drawn) / static_cast<double>(total);
}
#endif // __APPLE__

} // namespace

#ifdef __APPLE__
TEST(WaveformRenderPixelTest, HeadlessGroundTruth) {
    CGLContextObj ctx = makeContext();
    if (!ctx) {
        GTEST_SKIP() << "headless CGL context unavailable";
    }
    std::fprintf(stderr,
            "[pixel-test] renderer=%s version=%s\n",
            glGetString(GL_RENDERER),
            glGetString(GL_VERSION));

    WaveformPointer wf = makeWaveform();
    TrackPointer track = Track::newDummy(QStringLiteral("/t.wav"), TrackId());
    track->setWaveform(wf);

    TestWwr wwr;
    wwr.setTrack(track);
    wwr.resizeRenderer(kW, kH, 1.0f);

    allshader::WaveformRendererRGB renderer(&wwr,
            ::WaveformRendererAbstract::Play,
            ::WaveformRendererSignalBase::Option::None);
    renderer.setLowColor(QColor(255, 70, 70));
    renderer.setMidColor(QColor(70, 220, 70));
    renderer.setHighColor(QColor(80, 120, 255));
    renderer.setAxesColor(QColor(110, 110, 120));

    const double length = wwr.getLength();
    const double breadth = wwr.getBreadth();

    const QDir out(qEnvironmentVariable("MIGX_EYEBALL_DIR", QDir::currentPath()));
    out.mkpath(".");

    // Frame A.
    wwr.setWindow(0.30, 0.50);
    renderer.preprocess();
    const QImage a1 = renderToImage(renderer, length, breadth);
    ASSERT_FALSE(a1.isNull()) << "render produced no image (GL setup failed)";
    a1.save(out.filePath("waveform_A.png"));
    std::fprintf(stderr, "[pixel-test] wrote %s (drawn=%.3f)\n",
            out.filePath("waveform_A.png").toUtf8().constData(), drawnFraction(a1));
    EXPECT_GT(drawnFraction(a1), 0.02) << "waveform not visibly drawn";

    // Frame A again -- paused deck, idle-skip -> must be PIXEL-identical.
    renderer.preprocess();
    const QImage a2 = renderToImage(renderer, length, breadth);
    a2.save(out.filePath("waveform_A2.png"));
    EXPECT_EQ(a1, a2) << "a paused frame must render pixel-identically (idle-skip)";

    // Frame B -- playhead moved -> must render differently.
    wwr.setWindow(0.60, 0.80);
    renderer.preprocess();
    const QImage b = renderToImage(renderer, length, breadth);
    b.save(out.filePath("waveform_B.png"));
    EXPECT_NE(a1, b) << "a moved playhead must render a different image";

    CGLSetCurrentContext(nullptr);
    CGLDestroyContext(ctx);
}
#endif // __APPLE__
