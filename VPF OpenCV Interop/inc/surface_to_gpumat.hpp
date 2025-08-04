#pragma once

#include <memory>
#include <cstdint>
#include <opencv2/core/cuda.hpp>
#include "MemoryINterfaces.hpp"

namespace VPF {
    class Surface;
}

class SurfaceToGpuMatConverter {
public:
    // Yapıcı
    SurfaceToGpuMatConverter(std::shared_ptr<VPF::Surface> surface);

    // GPU matrisinin adresini döndüren fonksiyon
    uintptr_t GetGpuMatPtr(uint32_t plane_idx);

    // Boyutları ve pitch bilgilerini almak için yardımcı fonksiyonlar
    int GetWidth(uint32_t plane_idx);
    int GetHeight(uint32_t plane_idx);
    int GetPitch(uint32_t plane_idx);

    // GPU matrisini döndüren fonksiyon
    cv::cuda::GpuMat GetGpuMat(uint32_t plane_idx);

private:
    std::shared_ptr<VPF::Surface> surface_;  // Surface nesnesi
};
