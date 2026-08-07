// migx-analyze — headless BPM and key detection, printing JSON.
//
// Drives the *existing* analyzers (AnalyzerBeats, AnalyzerKey) rather than
// reimplementing them. A second detector in the CLI would be the
// parallel-implementation antipattern (P-11) and would be worse than the
// queen-mary/soundtouch code that already ships here.
//
// The pipeline mirrors what AnalyzerThread does, minus the threading:
//
//     SoundSourceProxy::openAudioSource -> readSampleFrames
//         -> Analyzer::processSamples (chunked)
//         -> Analyzer::storeResults(track) -> print
//
// Deliberately not real-time and never on the audio callback: this is a
// worker-thread-class batch tool (`arch-analyzer`, thread_domain: worker).
//
//   migx-analyze <audio-file> [more...]
//
// Prints one JSON object per line: {"path":…,"bpm":…,"key":…,"duration":…}

#include <QCommandLineParser>
#include <QCoreApplication>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QTemporaryDir>
#include <QTextStream>
#include <cmath>
#include <memory>
#include <vector>

#include "analyzer/analyzerbeats.h"
#include "analyzer/analyzerkey.h"
#include "analyzer/analyzertrack.h"
#include "preferences/keydetectionsettings.h"
#include "preferences/usersettings.h"
#include "sources/soundsourceproxy.h"
#include "track/track.h"
#include "util/samplebuffer.h"

namespace {

constexpr SINT kFramesPerChunk = 4096;
// Buckets for the energy envelope. Enough resolution for a terminal
// sparkline and a phrase-level read of the arrangement; not a waveform.
constexpr int kEnergyBuckets = 64;

// Analysis must not depend on the user's saved preferences — the same file
// must produce the same answer on any machine. A throwaway config gives the
// analyzers their documented defaults.
UserSettingsPointer makeDefaultConfig(const QString& dir) {
    return UserSettingsPointer(new UserSettings(dir + "/migx-analyze.cfg"));
}

QJsonObject analyzeOne(const QString& path, UserSettingsPointer pConfig) {
    QJsonObject out;
    out["path"] = path;

    TrackPointer pTrack = Track::newTemporary(path);
    if (!pTrack) {
        out["error"] = "could not open track";
        return out;
    }

    // AnalyzerThread opens with an explicit channel count; the plugins
    // DEBUG_ASSERT on (length % kAnalysisChannels == 0), so a source opened
    // with a different layout feeds them mis-strided audio.
    mixxx::AudioSource::OpenParams openParams;
    openParams.setChannelCount(mixxx::kAnalysisMaxChannels);
    auto pAudioSource = SoundSourceProxy(pTrack).openAudioSource(openParams);
    if (!pAudioSource) {
        out["error"] = "no decoder for this file";
        return out;
    }

    const auto sampleRate = pAudioSource->getSignalInfo().getSampleRate();
    const auto channelCount = pAudioSource->getSignalInfo().getChannelCount();
    const SINT frameLength = pAudioSource->frameLength();
    out["duration_s"] = frameLength / static_cast<double>(sampleRate);
    out["sample_rate"] = static_cast<int>(sampleRate);
    out["channels"] = static_cast<int>(channelCount);

    std::vector<AnalyzerPtr> analyzers;
    analyzers.push_back(std::make_unique<AnalyzerBeats>(pConfig, true));
    analyzers.push_back(
            std::make_unique<AnalyzerKey>(KeyDetectionSettings(pConfig)));

    const AnalyzerTrack analyzerTrack(pTrack);
    std::vector<Analyzer*> active;
    for (auto& pAnalyzer : analyzers) {
        if (pAnalyzer->initialize(
                    analyzerTrack, sampleRate, channelCount, frameLength)) {
            active.push_back(pAnalyzer.get());
        }
    }
    if (active.empty()) {
        out["error"] = "no analyzer accepted this track";
        return out;
    }

    // Summarise the decode into an RMS envelope while we are streaming it.
    // This is NOT a reimplementation of AnalyzerWaveform: that produces a
    // multi-band waveform for GPU rendering and needs a database handle. This
    // is a 64-bucket loudness summary of samples already passing through, for
    // a sparkline. Written under the same `energy_curve` key so the richer
    // version can replace it.
    std::vector<double> energySum(kEnergyBuckets, 0.0);
    std::vector<SINT> energyCount(kEnergyBuckets, 0);

    // Decode straight through once and fan each chunk out to every analyzer,
    // so a five-minute track is decoded once rather than once per analyzer.
    mixxx::SampleBuffer buffer(kFramesPerChunk * channelCount);
    SINT frameIndex = 0;
    while (frameIndex < frameLength) {
        const SINT framesToRead =
                std::min<SINT>(kFramesPerChunk, frameLength - frameIndex);
        const auto readable = pAudioSource->readSampleFrames(
                mixxx::WritableSampleFrames(
                        mixxx::IndexRange::forward(frameIndex, framesToRead),
                        mixxx::SampleBuffer::WritableSlice(
                                buffer.data(), buffer.size())));
        // readableLength() is in SAMPLES (interleaved), frameLength() is in
        // FRAMES. Treating one as the other feeds processSamples twice the
        // real count and advances the cursor twice as fast — which a periodic
        // click survives and real music does not.
        const SINT sampleCount = readable.readableLength();
        const SINT framesRead = sampleCount / channelCount;
        if (framesRead <= 0) {
            break;
        }
        for (Analyzer* pAnalyzer : active) {
            pAnalyzer->processSamples(
                    readable.readableData(), sampleCount);
        }

        const int bucket = std::min(kEnergyBuckets - 1,
                static_cast<int>(
                        (frameIndex * kEnergyBuckets) / std::max<SINT>(1, frameLength)));
        const CSAMPLE* pSamples = readable.readableData();
        double sumSquares = 0.0;
        for (SINT i = 0; i < sampleCount; ++i) {
            sumSquares += static_cast<double>(pSamples[i]) * pSamples[i];
        }
        energySum[bucket] += sumSquares;
        energyCount[bucket] += sampleCount;

        frameIndex += framesRead;
    }

    for (Analyzer* pAnalyzer : active) {
        pAnalyzer->storeResults(pTrack);
        pAnalyzer->cleanup();
    }

    const double bpm = pTrack->getBpm();
    if (bpm > 0.0) {
        out["bpm"] = bpm;
    }
    const QString keyText = pTrack->getKeyText();
    if (!keyText.isEmpty()) {
        out["key"] = keyText;
    }

    // Normalised 0..1 so a sparkline is comparable across tracks of very
    // different mastering levels.
    QJsonArray energy;
    double peak = 0.0;
    std::vector<double> rms(kEnergyBuckets, 0.0);
    for (int i = 0; i < kEnergyBuckets; ++i) {
        if (energyCount[i] > 0) {
            rms[i] = std::sqrt(energySum[i] / energyCount[i]);
            peak = std::max(peak, rms[i]);
        }
    }
    if (peak > 0.0) {
        for (int i = 0; i < kEnergyBuckets; ++i) {
            energy.append(std::round(rms[i] / peak * 1000.0) / 1000.0);
        }
        QJsonObject curve;
        curve["all"] = energy;
        out["energy_curve"] = curve;
    }
    return out;
}

} // namespace

int main(int argc, char* argv[]) {
    QCoreApplication app(argc, argv);
    QCoreApplication::setApplicationName("migx-analyze");

    QCommandLineParser parser;
    parser.setApplicationDescription(
            "Headless BPM/key analysis using Migx's own analyzers.");
    parser.addHelpOption();
    parser.addPositionalArgument("files", "Audio files to analyze.", "FILE...");
    parser.process(app);

    const QStringList files = parser.positionalArguments();
    if (files.isEmpty()) {
        parser.showHelp(2);
    }

    QTemporaryDir configDir;
    if (!configDir.isValid()) {
        QTextStream(stderr) << "could not create a temporary config dir\n";
        return 1;
    }
    auto pConfig = makeDefaultConfig(configDir.path());
    SoundSourceProxy::registerProviders();

    QTextStream stdoutStream(stdout);
    int failures = 0;
    for (const QString& path : files) {
        const QJsonObject result = analyzeOne(path, pConfig);
        if (result.contains("error")) {
            ++failures;
        }
        stdoutStream << QString::fromUtf8(
                                QJsonDocument(result).toJson(
                                        QJsonDocument::Compact))
                     << "\n";
        stdoutStream.flush();
    }
    return failures == 0 ? 0 : 1;
}
