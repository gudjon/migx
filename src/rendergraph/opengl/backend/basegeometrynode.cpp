#include "backend/basegeometrynode.h"

#include <QOpenGLContext>
#include <QOpenGLTexture>
#include <stdexcept>

#include "backend/shadercache.h"
#include "rendergraph/engine.h"
#include "rendergraph/geometrynode.h"
#include "rendergraph/texture.h"

using namespace rendergraph;

namespace {
GLenum toGlDrawingMode(DrawingMode mode) {
    switch (mode) {
    case DrawingMode::Triangles:
        return GL_TRIANGLES;
    case DrawingMode::TriangleStrip:
        return GL_TRIANGLE_STRIP;
    default:
        throw std::runtime_error("not implemented");
    }
}
} // namespace

BaseGeometryNode::~BaseGeometryNode() {
    // The VBO is only ever created while a context is current (in render()).
    // If no context is current at teardown, the context that owned the buffer
    // has already been destroyed and reclaimed the buffer with it, so there is
    // nothing to delete (and deleting would be undefined). Only free the name
    // when a live context is present.
    if (m_vboId != 0 && QOpenGLContext::currentContext() != nullptr) {
        glDeleteBuffers(1, &m_vboId);
    }
}

void BaseGeometryNode::initialize() {
    initializeOpenGLFunctions();
    GeometryNode* pThis = static_cast<GeometryNode*>(this);
    pThis->material().setShader(ShaderCache::getShaderForMaterial(&pThis->material()));
    pThis->material().setUniform(0, engine()->matrix());
}

void BaseGeometryNode::render() {
    GeometryNode* pThis = static_cast<GeometryNode*>(this);
    Geometry& geometry = pThis->geometry();
    Material& material = pThis->material();

    if (geometry.vertexCount() == 0) {
        return;
    }

    QOpenGLShaderProgram& shader = material.shader();
    VERIFY_OR_DEBUG_ASSERT(shader.bind()) {
        // if the shader can't be bound, don't try to render with it.
        // this should only happen if the shader compilation failed,
        // which shouldn't happen
        return;
    }

    glEnable(GL_BLEND);
    // Note: Qt scenegraph uses premultiplied alpha color in the shader,
    // so we need to do the same.
    glBlendFunc(GL_ONE, GL_ONE_MINUS_SRC_ALPHA);

    if (material.clearUniformsCacheDirty() || !material.isLastModifierOfShader()) {
        material.modifyShader();
        const UniformsCache& cache = material.uniformsCache();
        for (int i = 0; i < cache.count(); i++) {
            int location = material.uniformLocation(i);
            switch (cache.type(i)) {
            case Type::UInt:
                shader.setUniformValue(location, cache.get<GLuint>(i));
                break;
            case Type::Float:
                shader.setUniformValue(location, cache.get<GLfloat>(i));
                break;
            case Type::Vector2D:
                shader.setUniformValue(location, cache.get<QVector2D>(i));
                break;
            case Type::Vector3D:
                shader.setUniformValue(location, cache.get<QVector3D>(i));
                break;
            case Type::Vector4D:
                shader.setUniformValue(location, cache.get<QVector4D>(i));
                break;
            case Type::Matrix4x4:
                shader.setUniformValue(location, cache.get<QMatrix4x4>(i));
                break;
            }
        }
    }

    // Persistent VBO (P-22 / AP-12): upload the client-side vertex data into a
    // GL buffer object and re-upload it only when the geometry was marked dirty
    // or its size changed. glDrawArrays then sources vertices from GPU memory.
    // The previous no-VBO path bound client memory via setAttributeArray(),
    // which forced the driver to copy the entire vertex buffer CPU->GPU on
    // *every* draw; with a persistent buffer an unchanged waveform (paused deck,
    // static window) is drawn with zero upload.
    const int vertexBytes = geometry.vertexCount() * geometry.sizeOfVertex();
    if (m_vboId == 0) {
        glGenBuffers(1, &m_vboId);
        // Fresh buffer: force an (re)allocating upload below.
        m_vboByteSize = 0;
        m_geometryDirty = true;
    }
    glBindBuffer(GL_ARRAY_BUFFER, m_vboId);
    if (m_geometryDirty || vertexBytes != m_vboByteSize) {
        if (vertexBytes != m_vboByteSize) {
            // Storage size changed: (re)allocate and fill in one call.
            glBufferData(GL_ARRAY_BUFFER,
                    vertexBytes,
                    geometry.vertexData(),
                    GL_DYNAMIC_DRAW);
            m_vboByteSize = vertexBytes;
        } else {
            // Same size, new contents: orphan the old storage (so the driver
            // need not stall waiting for in-flight draws) then refill.
            glBufferData(GL_ARRAY_BUFFER, vertexBytes, nullptr, GL_DYNAMIC_DRAW);
            glBufferSubData(GL_ARRAY_BUFFER, 0, vertexBytes, geometry.vertexData());
        }
        m_geometryDirty = false;
    }

    // TODO this code assumes all vertices are floats
    int vertexOffset = 0;
    for (int i = 0; i < geometry.attributeCount(); i++) {
        const Geometry::Attribute& attribute = geometry.attributes()[i];
        int location = material.attributeLocation(i);
        shader.enableAttributeArray(location);
        // Offset into the currently bound VBO (bytes), not a client pointer.
        shader.setAttributeBuffer(location,
                GL_FLOAT,
                vertexOffset * static_cast<int>(sizeof(float)),
                attribute.m_tupleSize,
                geometry.sizeOfVertex());
        vertexOffset += attribute.m_tupleSize;
    }

    // TODO multiple textures
    auto* pTexture = material.texture(1);
    if (pTexture) {
        pTexture->backendTexture()->bind();
    }

    glDrawArrays(toGlDrawingMode(geometry.drawingMode()), 0, geometry.vertexCount());

    if (pTexture) {
        pTexture->backendTexture()->release();
    }

    for (int i = 0; i < geometry.attributeCount(); i++) {
        int location = material.attributeLocation(i);
        shader.disableAttributeArray(location);
    }

    // Restore the default (no VBO bound) so any client-array GL code elsewhere
    // is unaffected.
    glBindBuffer(GL_ARRAY_BUFFER, 0);

    shader.release();
}

void BaseGeometryNode::resize(int, int) {
    VERIFY_OR_DEBUG_ASSERT(engine() != nullptr) {
        return;
    }
    GeometryNode* pThis = static_cast<GeometryNode*>(this);
    pThis->material().setUniform(0, engine()->matrix());
}
