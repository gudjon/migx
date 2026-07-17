#pragma once

#include <QOpenGLFunctions>

#include "backend/basenode.h"

namespace rendergraph {
class BaseGeometryNode;
}  // namespace rendergraph

class rendergraph::BaseGeometryNode : public rendergraph::BaseNode,
                                      public QOpenGLFunctions {
  public:
    BaseGeometryNode() = default;
    ~BaseGeometryNode() override;

    // Called by Engine.
    void initialize() override;
    void render() override;
    void resize(int w, int h) override;

    // Marks the vertex data as changed so the next render() re-uploads it to
    // the persistent VBO. Driven by GeometryNode::markDirtyGeometry() -- the
    // same DirtyGeometry signal the scenegraph backend already requires for a
    // geometry update to become visible. Honoring it here makes the two
    // backends consistent (a renderer that mutates geometry without marking it
    // dirty is already broken on the QML/scenegraph path).
    void markGeometryDirty() {
        m_geometryDirty = true;
    }

  private:
    // Persistent GL_ARRAY_BUFFER holding the vertex data on the GPU.
    // 0 means "not created yet" (created lazily on first render()).
    GLuint m_vboId{0};
    // Byte size of the buffer's current storage, so we know when the vertex
    // count changed and the storage must be reallocated rather than refilled.
    int m_vboByteSize{0};
    // Set true whenever the client-side vertex data changed and must be
    // re-uploaded. Starts true so the first render() always uploads.
    bool m_geometryDirty{true};
};
