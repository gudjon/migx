#pragma once

// EngineBridge — accept CLI/agent intents over a local socket and turn them
// into deck actions. The C++ half of the contract defined and tested in
// tools/migx-cli/migx_cli/engine.py.
//
// Built as part of mixxx-lib. NOT yet constructed by anything — no call site
// creates an EngineBridge, so it compiles and links but never listens. The
// remaining step is deciding where it is owned (MixxxMainWindow, alongside the
// controller manager) and calling listen(). Until then this is inert code, not
// a working feature.
//
// Thread domain: MAIN/GUI thread only. QLocalServer is a Qt event-loop object
// and every write goes through ControlProxy, exactly as a MIDI controller
// mapping does. Nothing here may ever be called from process*() — P-02 is
// absolute, and an audio callback that touched a socket would be a hard
// regression, not a slow path.
//
// Ownership (P-06): the bridge is a PEER input surface, not an owner. Deck
// controls like [ChannelN],play already have several concurrent writers (GUI,
// keyboard, controller scripts). The engine owns the authoritative STATE; the
// bridge only requests changes and reads the result back.

#include <QJsonObject>
#include <QLocalServer>
#include <QLocalSocket>
#include <QObject>
#include <QString>

#include "preferences/usersettings.h"
#include "util/parented_ptr.h"

class PlayerManager;

class EngineBridge : public QObject {
    Q_OBJECT
  public:
    EngineBridge(PlayerManager* pPlayerManager, QObject* pParent = nullptr);
    ~EngineBridge() override;

    // Returns false (and logs) if the socket cannot be created. A bridge that
    // silently fails to listen would leave the CLI reporting "not-running"
    // forever with no clue why — P-34.
    bool listen(const QString& socketPath);

    // Where the socket lives when no path is given. Must match
    // migx_cli.engine.DEFAULT_SOCKET.
    static QString defaultSocketPath();

  private slots:
    void slotNewConnection();
    void slotReadyRead();

  private:
    QJsonObject dispatch(const QJsonObject& request);
    QJsonObject cmdLoad(const QJsonObject& request);
    QJsonObject cmdStatus(const QJsonObject& request);

    // Reads the deck's CURRENT control values. The receipt must describe what
    // the engine actually did, never an echo of the request: the DJ can move
    // the hardware in the same instant.
    QJsonObject deckReceipt(const QString& group) const;

    parented_ptr<QLocalServer> m_pServer;
    PlayerManager* m_pPlayerManager;  // not owned; outlives the bridge
};
