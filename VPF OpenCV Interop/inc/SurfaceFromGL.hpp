#pragma once

#include <memory>

#include "MemoryInterfaces.hpp"
#include <opencv2/core/cuda.hpp>
#include <opencv2/cudaimgproc.hpp>
#include <cuda.h>
#include <cuda_runtime.h>
#include <cuda_gl_interop.h>
#include <npp.h>
#include <nppi.h>
#include <nppi_color_conversion.h>

class SurfaceFromGL {
public:
    SurfaceFromGL(uint32_t width, uint32_t height, Pixel_Format format = Pixel_Format::RGB);

    std::shared_ptr<VPF::Surface> ConvertFromTexture(GLuint texture);

    ~SurfaceFromGL();

private:
    uint32_t width;
    uint32_t height;
    Pixel_Format pixelFormat;

    cudaGraphicsResource* cudaResource = nullptr;

    void RegisterTexture(GLuint texture);
    void UnregisterTexture();
};
