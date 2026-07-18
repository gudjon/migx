#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>

#include <algorithm>

#include "test/librarytest.h"
#include "track/globaltrackcache.h"
#include "track/track.h"
#include "waveform/waveform.h"

using ::testing::UnorderedElementsAre;

class TrackDAOTest : public LibraryTest {
};

namespace {

WaveformPointer makeSidecarTestWaveform() {
    constexpr int sampleRate = 44100;
    const auto frameLength = static_cast<SINT>(sampleRate) * 16;
    auto pWaveform = WaveformPointer(new Waveform(sampleRate, frameLength, 441, -1, 0));
    const int dataSize = pWaveform->getDataSize();
    WaveformData* pData = pWaveform->data();
    for (int i = 0; i < dataSize; ++i) {
        const auto value = static_cast<unsigned char>(
                (i * 255) / std::max(1, dataSize - 1));
        pData[i].filtered.low = value / 2;
        pData[i].filtered.mid = value;
        pData[i].filtered.high = 255 - value;
        pData[i].filtered.all = value;
    }
    pWaveform->setCompletion(dataSize);
    return pWaveform;
}

QJsonObject readJsonObject(const QString& filePath) {
    QFile file(filePath);
    if (!file.open(QIODevice::ReadOnly)) {
        return {};
    }
    const QJsonDocument doc = QJsonDocument::fromJson(file.readAll());
    if (!doc.isObject()) {
        return {};
    }
    return doc.object();
}

} // namespace


TEST_F(TrackDAOTest, detectMovedTracks) {
    TrackDAO& trackDAO = internalCollection()->getTrackDAO();

    QString filename = QStringLiteral("file.mp3");

    mixxx::FileInfo oldFile(QDir(QDir::tempPath() + QStringLiteral("/old/dir1")), filename);
    mixxx::FileInfo newFile(QDir(QDir::tempPath() + QStringLiteral("/new/dir1")), filename);
    mixxx::FileInfo otherFile(QDir(QDir::tempPath() + QStringLiteral("/new")), filename);

    TrackPointer pOldTrack = Track::newTemporary(mixxx::FileAccess(oldFile));
    TrackPointer pNewTrack = Track::newTemporary(mixxx::FileAccess(newFile));
    TrackPointer pOtherTrack = Track::newTemporary(mixxx::FileAccess(otherFile));

    // Arbitrary duration
    pOldTrack->setDuration(135);
    pNewTrack->setDuration(135.7);
    pOtherTrack->setDuration(135.7);

    TrackId oldId = internalCollection()->addTrack(pOldTrack, false);
    TrackId newId = internalCollection()->addTrack(pNewTrack, false);
    internalCollection()->addTrack(pOtherTrack, false);

    // Mark as missing
    QSqlQuery query(dbConnection());
    query.prepare("UPDATE track_locations SET fs_deleted=1 WHERE location=:location");
    query.bindValue(":location", oldFile.location());
    query.exec();

    QList<RelocatedTrack> relocatedTracks;
    QStringList addedTracks(newFile.location());
    bool cancel = false;
    trackDAO.detectMovedTracks(&relocatedTracks, addedTracks, &cancel);

    QSet<TrackId> updatedTrackIds;
    QSet<TrackId> removedTrackIds;
    for (const auto& relocatedTrack : std::as_const(relocatedTracks)) {
        updatedTrackIds.insert(relocatedTrack.updatedTrackRef().getId());
        removedTrackIds.insert(relocatedTrack.deletedTrackId());
    }

    EXPECT_THAT(updatedTrackIds, UnorderedElementsAre(oldId));
    EXPECT_THAT(removedTrackIds, UnorderedElementsAre(newId));

    QSet<QString> trackLocations = trackDAO.getAllTrackLocations();
    EXPECT_THAT(trackLocations, UnorderedElementsAre(newFile.location(), otherFile.location()));
}

// Regression test for the bug where a BPM-locked track without a beatgrid
// loses its lock when reloaded from the database.
// https://github.com/mixxxdj/mixxx/issues/15196
TEST_F(TrackDAOTest, bpmLockPreservedForTrackWithoutBeats) {
    const mixxx::FileInfo fileInfo(
            QDir(QDir::tempPath()), QStringLiteral("bpmlocked-no-beats.mp3"));
    TrackPointer pTrack = Track::newTemporary(mixxx::FileAccess(fileInfo));
    pTrack->setDuration(135);
    // Lock the BPM although the track has no beatgrid at all.
    pTrack->setBpmLocked(true);
    ASSERT_FALSE(pTrack->getBeats());
    ASSERT_TRUE(pTrack->isBpmLocked());

    const TrackId trackId = internalCollection()->addTrack(pTrack, false);
    ASSERT_TRUE(trackId.isValid());

    // Dropping the last reference evicts the track from the cache
    // synchronously (eviction runs as a direct call on this thread), so the
    // lookup below reloads it from the database instead of returning the
    // cached in-memory object whose lock flag was never lost.
    pTrack.reset();
    ASSERT_TRUE(GlobalTrackCacheLocker().isEmpty());

    const TrackPointer pReloaded = internalCollection()->getTrackById(trackId);
    ASSERT_TRUE(pReloaded);
    EXPECT_FALSE(pReloaded->getBeats());
    EXPECT_TRUE(pReloaded->isBpmLocked());
}

TEST_F(TrackDAOTest, saveTrackExportsSidecarCuesAndEnergy) {
    const QString trackLocation =
            getTestDataDir().filePath(QStringLiteral("sidecar-cues-energy.wav"));
    TrackPointer pTrack = Track::newTemporary(
            mixxx::FileAccess(mixxx::FileInfo(trackLocation)));
    pTrack->setAudioProperties(
            mixxx::audio::ChannelCount(2),
            mixxx::audio::SampleRate(44100),
            mixxx::audio::Bitrate(),
            mixxx::Duration::fromSeconds(120));
    ASSERT_TRUE(pTrack->trySetBpm(120.0));
    pTrack->setKeyText(QStringLiteral("E minor"));
    pTrack->setWaveform(makeSidecarTestWaveform());

    const TrackId trackId = internalCollection()->addTrack(pTrack, false);
    ASSERT_TRUE(trackId.isValid());

    CuePointer pCue = pTrack->createAndAddCue(mixxx::CueType::HotCue,
            0,
            mixxx::audio::FramePos(44100),
            mixxx::audio::kInvalidFramePos);
    pCue->setLabel(QStringLiteral("mix in"));

    ASSERT_TRUE(internalCollection()->saveTrack(pTrack.get()));

    const QJsonObject root =
            readJsonObject(trackLocation + QStringLiteral(".migx/track.json"));
    ASSERT_FALSE(root.isEmpty());
    EXPECT_DOUBLE_EQ(root.value(QStringLiteral("bpm")).toDouble(), 120.0);
    EXPECT_EQ(root.value(QStringLiteral("key")).toString(), QStringLiteral("Em"));

    const QJsonArray cues = root.value(QStringLiteral("cues")).toArray();
    ASSERT_EQ(cues.size(), 1);
    const QJsonObject cue = cues.at(0).toObject();
    EXPECT_EQ(cue.value(QStringLiteral("type")).toString(), QStringLiteral("hotcue"));
    EXPECT_EQ(cue.value(QStringLiteral("hotcue")).toInt(), 0);
    EXPECT_EQ(cue.value(QStringLiteral("label")).toString(), QStringLiteral("mix in"));
    EXPECT_DOUBLE_EQ(cue.value(QStringLiteral("position_frames")).toDouble(), 44100.0);
    EXPECT_DOUBLE_EQ(cue.value(QStringLiteral("position_ms")).toDouble(), 1000.0);
    EXPECT_DOUBLE_EQ(cue.value(QStringLiteral("position_beats")).toDouble(), 2.0);

    const QJsonObject energyCurve = root.value(QStringLiteral("energy_curve")).toObject();
    EXPECT_EQ(energyCurve.value(QStringLiteral("unit")).toString(),
            QStringLiteral("track_fraction"));
    EXPECT_EQ(energyCurve.value(QStringLiteral("method")).toString(),
            QStringLiteral("waveform-filtered-downsample-v1"));
    const QJsonArray samples = energyCurve.value(QStringLiteral("samples")).toArray();
    ASSERT_EQ(samples.size(), 32);
    EXPECT_LT(samples.at(0).toDouble(),
            samples.at(samples.size() - 1).toDouble());

    const QJsonObject bands = energyCurve.value(QStringLiteral("bands")).toObject();
    EXPECT_EQ(bands.value(QStringLiteral("low")).toArray().size(), samples.size());
    EXPECT_EQ(bands.value(QStringLiteral("mid")).toArray().size(), samples.size());
    EXPECT_EQ(bands.value(QStringLiteral("high")).toArray().size(), samples.size());
    EXPECT_EQ(bands.value(QStringLiteral("all")).toArray().size(), samples.size());
}
