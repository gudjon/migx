# Architecture — DUI (draft)

```text
res/design/DESIGN.md  →  (gen or manual)  →  res/qml/Theme.qml (pragma Singleton)
                                                      ↓
                                              res/qml/* controls
```

- Theme is **GUI-thread only** (QML).  
- ADR-004: QML-primary shell.  
- Generator stays build/dev dependency (Node design.md CLI optional).
