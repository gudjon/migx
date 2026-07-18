// Correctness regression for the Wave-2a idle-frame skip in
// allshader::WaveformRendererRGB::preprocessInner() (EVD-0004).
//
// The optimization skips the per-frame vertex rebuild when every geometry-
// shaping input is unchanged. Its only failure mode is an INCOMPLETE input
// cache key -> a stale waveform (skip when it should have rebuilt). These tests
// pin the correctness contract by comparing the produced vertex buffer:
//   - identical frame  -> identical output (skip is bit-safe);
//   - position changed -> output changes (position is in the key);
//   - back to the first position -> output matches the original;
//   - size changed     -> vertex count changes (size is in the key).
// The BM_WaveformRGBStatic benchmark separately proves the skip actually fires
// (~31us -> ~0.04us); these tests prove it stays correct.

#include <gtest/gtest.h>

#include <QString>
#include <cstdint>
#include <vector>

#include "rendergraph/geometry.h"
#include "track/track.h"
#include "waveform/renderers/allshader/waveformrendererrgb.h"
#include "waveform/renderers/waveformrendererabstract.h"
#include "waveform/renderers/waveformwidgetrenderer.h"
#include "waveform/waveform.h"

namespace {

using namespace rendergraph;

constexpr int kWidth = 1920;
constexpr int kHeight = 200;
constexpr float kDevicePixelRatio = 2.0f;

// Exposes the displayed window so the test can move the "playhead" without the
// full ControlObject / VSync plumbing (mirrors the benchmark helper).
class TestWaveformWidgetRenderer : public WaveformWidgetRenderer {
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
    auto pWaveform = WaveformPointer(new Waveform(sampleRate, frameLength, 441, -1, 0));
    const int dataSize = pWaveform->getDataSize();
    WaveformData* pData = pWaveform->data();
    uint32_t lcg = 0x1234567u;
    for (int i = 0; i < dataSize; ++i) {
        lcg = lcg * 1664525u + 1013904223u;
        pData[i].filtered.low = static_cast<unsigned char>((lcg >> 8) & 0xFF);
        pData[i].filtered.mid = static_cast<unsigned char>((lcg >> 16) & 0xFF);
        pData[i].filtered.high = static_cast<unsigned char>((lcg >> 24) & 0xFF);
        pData[i].filtered.all = static_cast<unsigned char>(lcg & 0xFF);
    }
    pWaveform->setCompletion(dataSize);
    return pWaveform;
}

std::vector<char> snapshot(const Geometry& geometry) {
    const int bytes = geometry.vertexCount() * geometry.sizeOfVertex();
    const char* p = reinterpret_cast<const char*>(geometry.vertexData());
    return std::vector<char>(p, p + bytes);
}

} // namespace

TEST(WaveformRendererRGBIdleSkipTest, SkipIsBitSafeAndKeyInvalidates) {
    WaveformPointer pWaveform = makeWaveform();
    TrackPointer pTrack = Track::newDummy(QStringLiteral("/t.wav"), TrackId());
    pTrack->setWaveform(pWaveform);

    TestWaveformWidgetRenderer wwr;
    wwr.setTrack(pTrack);
    wwr.resizeRenderer(kWidth, kHeight, kDevicePixelRatio);

    allshader::WaveformRendererRGB renderer(&wwr,
            ::WaveformRendererAbstract::Play,
            ::WaveformRendererSignalBase::Option::None);

    // Window A -> first build.
    wwr.setWindow(0.40, 0.60);
    renderer.preprocess();
    const std::vector<char> a1 = snapshot(renderer.geometry());
    ASSERT_FALSE(a1.empty());

    // Identical frame: whether skipped or rebuilt, the output must be identical.
    renderer.preprocess();
    EXPECT_EQ(a1, snapshot(renderer.geometry()))
            << "an unchanged frame must not change the geometry";

    // Position moved (same zoom): the waveform region differs -> must rebuild.
    wwr.setWindow(0.20, 0.40);
    renderer.preprocess();
    const std::vector<char> b = snapshot(renderer.geometry());
    EXPECT_NE(a1, b)
            << "a position change must rebuild (position is in the cache key)";

    // Back to window A -> output must match the original build exactly.
    wwr.setWindow(0.40, 0.60);
    renderer.preprocess();
    EXPECT_EQ(a1, snapshot(renderer.geometry()))
            << "returning to a prior frame must reproduce its geometry";

    // Widget resized: pixel count changes -> vertex count must change.
    wwr.resizeRenderer(kWidth / 2, kHeight, kDevicePixelRatio);
    renderer.preprocess();
    EXPECT_NE(a1.size(), snapshot(renderer.geometry()).size())
            << "a size change must rebuild (size is in the cache key)";
}
