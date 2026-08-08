#include "bridge/enginebridge.h"

#include <QDir>
#include <QFileInfo>
#include <QJsonDocument>
#include <QStandardPaths>

#include "control/controlobject.h"
#include "control/controlproxy.h"
#include "mixer/playermanager.h"
#include "moc_enginebridge.cpp"

namespace {
// Read back after every intent, so a receipt is engine truth. Must match
// migx_cli.engine.RECEIPT_KEYS.
const QStringList kReceiptKeys = {
        QStringLiteral("play"),
        QStringLiteral("bpm"),
        QStringLiteral("rate"),
        QStringLiteral("duration"),
        QStringLiteral("playposition"),
        QStringLiteral("track_loaded"),
};

QJsonObject fail(const QString& status, const QString& error) {
    QJsonObject out;
    out["ok"] = false;
    out["status"] = status;
    out["error"] = error;
    return out;
}
} // namespace

EngineBridge::EngineBridge(PlayerManager* pPlayerManager, QObject* pParent)
        : QObject(pParent),
          m_pServer(make_parented<QLocalServer>(this)),
          m_pPlayerManager(pPlayerManager) {
    connect(m_pServer,
            &QLocalServer::newConnection,
            this,
            &EngineBridge::slotNewConnection);
}

EngineBridge::~EngineBridge() {
    if (m_pServer->isListening()) {
        const QString name = m_pServer->fullServerName();
        m_pServer->close();
        // A stale socket file makes the CLI think an engine is listening when
        // none is. Remove it on the way out.
        QLocalServer::removeServer(name);
    }
}

QString EngineBridge::defaultSocketPath() {
    // Under the app data dir, NOT /tmp: /tmp is world-writable and this socket
    // accepts commands that move audio.
    const QString dir =
            QStandardPaths::writableLocation(QStandardPaths::AppDataLocation);
    return QDir(dir).filePath(QStringLiteral("engine.sock"));
}

bool EngineBridge::listen(const QString& socketPath) {
    const QString path = socketPath.isEmpty() ? defaultSocketPath() : socketPath;
    QDir().mkpath(QFileInfo(path).absolutePath());
    // A socket file left by a crashed run would block bind; removeServer only
    // deletes it when nothing is actually listening.
    QLocalServer::removeServer(path);
    if (!m_pServer->listen(path)) {
        qWarning() << "EngineBridge: cannot listen on" << path << ":"
                   << m_pServer->errorString();
        return false;
    }
    qInfo() << "EngineBridge listening on" << path;
    return true;
}

void EngineBridge::slotNewConnection() {
    while (QLocalSocket* pConn = m_pServer->nextPendingConnection()) {
        connect(pConn, &QLocalSocket::readyRead, this, &EngineBridge::slotReadyRead);
        connect(pConn, &QLocalSocket::disconnected, pConn, &QLocalSocket::deleteLater);
    }
}

void EngineBridge::slotReadyRead() {
    auto* pConn = qobject_cast<QLocalSocket*>(sender());
    if (!pConn) {
        return;
    }
    // One JSON object per line. canReadLine() rather than readAll(): a client
    // write can arrive split, and parsing a half line would reject a valid
    // command.
    while (pConn->canReadLine()) {
        const QByteArray line = pConn->readLine().trimmed();
        if (line.isEmpty()) {
            continue;
        }
        QJsonParseError parseError;
        const QJsonDocument doc = QJsonDocument::fromJson(line, &parseError);
        QJsonObject reply;
        if (parseError.error != QJsonParseError::NoError || !doc.isObject()) {
            reply = fail(QStringLiteral("bad-request"), parseError.errorString());
        } else {
            reply = dispatch(doc.object());
        }
        pConn->write(QJsonDocument(reply).toJson(QJsonDocument::Compact) + '\n');
        pConn->flush();
    }
}

QJsonObject EngineBridge::dispatch(const QJsonObject& request) {
    const QString cmd = request.value(QStringLiteral("cmd")).toString();
    if (cmd == QLatin1String("load")) {
        return cmdLoad(request);
    }
    if (cmd == QLatin1String("status")) {
        return cmdStatus(request);
    }
    return fail(QStringLiteral("unknown-cmd"),
            QStringLiteral("no such command: ") + cmd);
}

QJsonObject EngineBridge::cmdLoad(const QJsonObject& request) {
    const QString group = request.value(QStringLiteral("group")).toString();
    const QString path = request.value(QStringLiteral("path")).toString();
    const bool play = request.value(QStringLiteral("play")).toBool(false);

    if (group.isEmpty() || path.isEmpty()) {
        return fail(QStringLiteral("bad-request"),
                QStringLiteral("load needs both group and path"));
    }
    if (!QFileInfo::exists(path)) {
        return fail(QStringLiteral("no-such-track"), path);
    }
    if (!m_pPlayerManager) {
        return fail(QStringLiteral("no-engine"),
                QStringLiteral("player manager unavailable"));
    }

    // The play flag rides along with the load: slotLoadLocationToPlayer starts
    // the deck as part of loading, so a separate [ChannelN],play write would
    // race the load.
    m_pPlayerManager->slotLoadLocationToPlayer(path, group, play);

    QJsonObject out = deckReceipt(group);
    out["ok"] = true;
    out["group"] = group;
    return out;
}

QJsonObject EngineBridge::cmdStatus(const QJsonObject& request) {
    const QString group = request.value(QStringLiteral("group")).toString();
    if (group.isEmpty()) {
        return fail(QStringLiteral("bad-request"),
                QStringLiteral("status needs a group"));
    }
    QJsonObject out = deckReceipt(group);
    out["ok"] = true;
    out["group"] = group;
    return out;
}

QJsonObject EngineBridge::deckReceipt(const QString& group) const {
    QJsonObject out;
    for (const QString& key : kReceiptKeys) {
        const ConfigKey configKey(group, key);
        // A control that does not exist is reported as null rather than 0.0:
        // "not present" and "zero" are different answers, and conflating them
        // is how a receipt starts lying (P-34).
        if (!ControlObject::exists(configKey)) {
            out[key] = QJsonValue();
            continue;
        }
        ControlProxy proxy(configKey);
        out[key] = proxy.get();
    }
    return out;
}
