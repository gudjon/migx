#pragma once

#include "rendergraph/geometrynode.h"
#include "util/class.h"
#include "waveform/renderers/allshader/waveformrenderersignalbase.h"

namespace allshader {
class WaveformRendererRGB;
} // namespace allshader

class allshader::WaveformRendererRGB final
        : public allshader::WaveformRendererSignalBase,
          public rendergraph::GeometryNode {
  public:
    explicit WaveformRendererRGB(WaveformWidgetRenderer* waveformWidget,
            ::WaveformRendererAbstract::PositionSource type =
                    ::WaveformRendererAbstract::Play,
            ::WaveformRendererSignalBase::Options options =
                    ::WaveformRendererSignalBase::Option::None);

    // Pure virtual from WaveformRendererSignalBase, not used
    void onSetup(const QDomNode& node) override;

    bool supportsSlip() const override {
        return true;
    }

    // Virtuals for rendergraph::Node
    void preprocess() override;

  private:
    bool m_isSlipRenderer;
    ::WaveformRendererSignalBase::Options m_options;

    // Wave-2 (MTL, EVD-0003): skip the full per-frame vertex rebuild when every
    // input that shapes the geometry is unchanged -- a paused/static deck
    // redrawing every vsync, the common idle case where preprocessInner() would
    // otherwise rebuild identical vertices and re-upload them. EVERY value read
    // by preprocessInner() below its guards MUST appear here (a missing field
    // would render a stale waveform); the defaulted operator== compares all
    // members, so nothing can be silently dropped from the comparison. Constant
    // inputs (m_maxValue, m_isSlipRenderer) are intentionally omitted.
    struct PreprocessInputs {
        const void* track = nullptr;
        const void* waveformData = nullptr;
        int completion = -1;
        int dataSize = 0;
        int length = 0;
        int pixelLength = 0;
        float devicePixelRatio = 0.f;
        double xVisualFrame = 0.0;
        double visualIncrementPerPixel = 0.0;
        float allGain = 0.f;
        float lowGain = 0.f;
        float midGain = 0.f;
        float highGain = 0.f;
        float breadth = 0.f;
        bool splitLeftRight = false;
        float axesR = 0.f, axesG = 0.f, axesB = 0.f;
        float lowR = 0.f, lowG = 0.f, lowB = 0.f;
        float midR = 0.f, midG = 0.f, midB = 0.f;
        float highR = 0.f, highG = 0.f, highB = 0.f;
        bool operator==(const PreprocessInputs&) const = default;
    };
    bool m_haveCachedInputs{false};
    PreprocessInputs m_cachedInputs;

    bool preprocessInner();

    DISALLOW_COPY_AND_ASSIGN(WaveformRendererRGB);
};
