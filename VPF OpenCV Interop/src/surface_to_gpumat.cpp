#include "surface_to_gpumat.hpp"
#include "NvCodecUtils.h"
#include "MemoryInterfaces.hpp"
#include <stdexcept>
#include <opencv2/core/cuda.hpp>

using namespace VPF;

SurfaceToGpuMatConverter::SurfaceToGpuMatConverter(std::shared_ptr<Surface> surface)
    : surface_(std::move(surface)) {
    if (!surface_ || surface_->Empty()) {
        throw std::runtime_error("Surface is null or empty.");
    }
}

uintptr_t SurfaceToGpuMatConverter::GetGpuMatPtr(uint32_t plane_idx) {
    // SurfacePlane nesnesini al
    SurfacePlane* plane = surface_->GetSurfacePlane(plane_idx);
    if (!plane || plane->GpuMem() == 0) {
        throw std::runtime_error("Invalid surface plane.");
    }
    return static_cast<uintptr_t>(plane->GpuMem());
}

int SurfaceToGpuMatConverter::GetWidth(uint32_t plane_idx) {
    // SurfacePlane nesnesini al
    SurfacePlane* plane = surface_->GetSurfacePlane(plane_idx);
    return plane ? plane->Width() : 0;
}

int SurfaceToGpuMatConverter::GetHeight(uint32_t plane_idx) {
    // SurfacePlane nesnesini al
    SurfacePlane* plane = surface_->GetSurfacePlane(plane_idx);
    return plane ? plane->Height() : 0;
}

int SurfaceToGpuMatConverter::GetPitch(uint32_t plane_idx) {
    // SurfacePlane nesnesini al
    SurfacePlane* plane = surface_->GetSurfacePlane(plane_idx);
    return plane ? plane->Pitch() : 0;
}

cv::cuda::GpuMat SurfaceToGpuMatConverter::GetGpuMat(uint32_t plane_idx) {
    // SurfacePlane nesnesini al
    SurfacePlane* plane = surface_->GetSurfacePlane(plane_idx);
    if (!plane || plane->GpuMem() == 0) {
        throw std::runtime_error("Invalid surface plane.");
    }

    CUdeviceptr gpu_ptr = plane->GpuMem(); // GPU Bellek Adresi

    // GpuMat'ı sıfır kopya (zero-copy) olarak oluştur
    return cv::cuda::GpuMat(
        plane->Height(),
        plane->Width(),
        CV_MAKETYPE(CV_8U, plane->ElemSize()),  // Veri tipi, örnek olarak uchar
        reinterpret_cast<void*>(gpu_ptr),      // GPU bellek adresini ata
        plane->Pitch()                          // Satır boyu (stride)
    );
}
