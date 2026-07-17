// Benchmark for the scalar IIR EQ-filter steady-state path (the DSP SIMD target).
//
// Every builtin EQ effect (parametric / graphic / biquad-full-kill / filter)
// runs EngineFilterIIR<SIZE,PASS>::process() over each audio buffer, per deck,
// on the real-time callback. The steady-state loop
// (src/engine/filters/enginefilteriir.h:241-244) is a scalar per-sample IIR
// difference equation, deinterleaved stereo (m_buf1 = L, m_buf2 = R). This is
// the NEON/Accelerate(vDSP) target of PS-DSP-01: a faster, allocation-free
// vector form must not regress this p99 and must stay numerically equivalent.
//
// Unlike the waveform render bench, this path never touches a GL context, so it
// measures COMPLETELY in the headless mixxx-test binary -- a full EVD-DSP-01
// baseline, not a partial one.
//
// Run: build/mixxx-test --benchmark --benchmark_filter=BM_EngineFilter

#include <benchmark/benchmark.h>

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <vector>

#include "engine/filters/enginefilterbessel4.h"
#include "engine/filters/enginefilterbiquad1.h"
#include "engine/filters/enginefilterbutterworth8.h"
#include "util/types.h"

namespace {

// One real-time audio buffer: 1024 stereo frames -> 2048 interleaved CSAMPLEs.
// process()'s bufferSize argument counts samples (it strides i += 2 for stereo).
constexpr std::size_t kFrames = 1024;
constexpr std::size_t kSamples = kFrames * 2;
constexpr int kSampleRate = 44100;

std::vector<CSAMPLE> makeSignal() {
    // Deterministic broadband input so the filter recurrence does real work
    // (a DC or silent buffer would be an unrealistic best case).
    std::vector<CSAMPLE> in(kSamples);
    uint32_t lcg = 0x2545f491u;
    for (auto& s : in) {
        lcg = lcg * 1664525u + 1013904223u;
        // [-1, 1) pseudo-random excitation.
        s = static_cast<CSAMPLE>(static_cast<int32_t>(lcg)) /
                static_cast<CSAMPLE>(2147483648.0);
    }
    return in;
}

// Sorts the per-buffer µs samples and reports p50/p90/p99/max counters + label.
void reportUs(benchmark::State& state, std::vector<double>& bufUs) {
    if (bufUs.empty()) {
        return;
    }
    std::sort(bufUs.begin(), bufUs.end());
    const auto pct = [&](double q) {
        const auto idx = static_cast<std::size_t>(
                q * static_cast<double>(bufUs.size() - 1) + 0.5);
        return bufUs[idx];
    };
    double sum = 0.0;
    for (double v : bufUs) {
        sum += v;
    }
    const double p50 = pct(0.50);
    const double p90 = pct(0.90);
    const double p99 = pct(0.99);
    const double maxv = bufUs.back();
    const double minv = bufUs.front();
    const double mean = sum / static_cast<double>(bufUs.size());

    state.counters["p50_us"] = p50;
    state.counters["p90_us"] = p90;
    state.counters["p99_us"] = p99;
    state.counters["max_us"] = maxv;
    state.counters["min_us"] = minv;
    state.counters["mean_us"] = mean;
    state.counters["frames_per_buf"] = static_cast<double>(kFrames);

    char label[256];
    std::snprintf(label,
            sizeof(label),
            "p50=%.3fus p90=%.3fus p99=%.3fus max=%.3fus min=%.3fus n=%zu",
            p50,
            p90,
            p99,
            maxv,
            minv,
            bufUs.size());
    state.SetLabel(label);
    state.SetItemsProcessed(static_cast<int64_t>(bufUs.size()));
}

// Times filter.process() once per bench iteration over a fixed buffer and
// reports the per-buffer time distribution (p50/p90/p99/max), the EVD-DSP-01
// input. The filter is settled first so we measure the steady-state path
// (enginefilteriir.h:241-244), not the one-shot ramp.
template<typename Filter>
void runFilter(benchmark::State& state, Filter& filter) {
    const std::vector<CSAMPLE> in = makeSignal();
    std::vector<CSAMPLE> out(kSamples);

    filter.assumeSettled(); // measure the steady-state loop, not the ramp path

    std::vector<double> bufUs;
    bufUs.reserve(1 << 16);

    for (auto _ : state) {
        const auto start = std::chrono::steady_clock::now();
        filter.process(in.data(), out.data(), kSamples);
        const auto end = std::chrono::steady_clock::now();

        benchmark::DoNotOptimize(out.data());
        benchmark::ClobberMemory();

        bufUs.push_back(
                std::chrono::duration<double, std::micro>(end - start).count());
    }
    reportUs(state, bufUs);
}

// SIZE=5, IIR_BP -- the biquad peaking band used by the parametric / graphic
// EQ effects (the most common per-band EQ filter).
void BM_EngineFilterBiquadPeaking(benchmark::State& state) {
    EngineFilterBiquad1Peaking filter(
            mixxx::audio::SampleRate(kSampleRate), 1000.0, 1.0);
    runFilter(state, filter);
}

// SIZE=8, IIR_LP -- a higher-order Butterworth low-pass (the deeper recurrence,
// where a vectorized form has the most headroom).
void BM_EngineFilterButterworth8Low(benchmark::State& state) {
    EngineFilterButterworth8Low filter(
            mixxx::audio::SampleRate(kSampleRate), 1000.0);
    runFilter(state, filter);
}

// Aggregate: the full BiquadFullKillEQEffect per-channel filter chain (the
// DEFAULT deck EQ), worst case with every band engaged. Per
// src/effects/backends/builtin/biquadfullkilleqeffect.h that is 8 IIR filters:
// the always-on LVMix isolator's 2 Bessel4 low-pass crossovers (the 3-band
// split) + 3 peaking boosts + (low-shelf + mid-peak + high-shelf) kills. This
// times ONE deck's whole EQ chain per buffer; EVD-DSP-01 scales it to 4 decks
// to settle the DSP Wave-2 (vDSP/NEON) go/no-go: if 4 decks of full EQ is still
// a negligible fraction of the buffer period, the SIMD rewrite is not worth it.
void BM_EngineFilterFullEqChain(benchmark::State& state) {
    const mixxx::audio::SampleRate sr(kSampleRate);
    EngineFilterBessel4Low isoLow(sr, 246.0);
    EngineFilterBessel4Low isoHigh(sr, 2453.0);
    EngineFilterBiquad1Peaking lowBoost(sr, 100.0, 0.4);
    EngineFilterBiquad1Peaking midBoost(sr, 1100.0, 0.4);
    EngineFilterBiquad1Peaking highBoost(sr, 10000.0, 0.4);
    EngineFilterBiquad1LowShelving lowKill(sr, 100.0, 0.4);
    EngineFilterBiquad1Peaking midKill(sr, 1100.0, 0.4);
    EngineFilterBiquad1HighShelving highKill(sr, 10000.0, 0.4);

    isoLow.assumeSettled();
    isoHigh.assumeSettled();
    lowBoost.assumeSettled();
    midBoost.assumeSettled();
    highBoost.assumeSettled();
    lowKill.assumeSettled();
    midKill.assumeSettled();
    highKill.assumeSettled();

    const std::vector<CSAMPLE> in = makeSignal();
    std::vector<CSAMPLE> a(kSamples);
    std::vector<CSAMPLE> b(kSamples);

    std::vector<double> bufUs;
    bufUs.reserve(1 << 16);

    for (auto _ : state) {
        const auto start = std::chrono::steady_clock::now();
        // 8 filters run over the buffer (ping-pong a<->b). Series vs parallel
        // topology does not change the total filter work being timed.
        isoLow.process(in.data(), a.data(), kSamples);
        isoHigh.process(a.data(), b.data(), kSamples);
        lowBoost.process(b.data(), a.data(), kSamples);
        midBoost.process(a.data(), b.data(), kSamples);
        highBoost.process(b.data(), a.data(), kSamples);
        lowKill.process(a.data(), b.data(), kSamples);
        midKill.process(b.data(), a.data(), kSamples);
        highKill.process(a.data(), b.data(), kSamples);
        const auto end = std::chrono::steady_clock::now();

        benchmark::DoNotOptimize(a.data());
        benchmark::ClobberMemory();

        bufUs.push_back(
                std::chrono::duration<double, std::micro>(end - start).count());
    }
    reportUs(state, bufUs);
}

} // namespace

// Fixed iteration count so two runs are directly comparable (reproducibility
// gate) and the percentile sample is stable.
BENCHMARK(BM_EngineFilterBiquadPeaking)
        ->Iterations(20000)
        ->Unit(benchmark::kMicrosecond)
        ->UseRealTime();
BENCHMARK(BM_EngineFilterButterworth8Low)
        ->Iterations(20000)
        ->Unit(benchmark::kMicrosecond)
        ->UseRealTime();
BENCHMARK(BM_EngineFilterFullEqChain)
        ->Iterations(20000)
        ->Unit(benchmark::kMicrosecond)
        ->UseRealTime();
