#include "SurfaceFromGL.hpp"
#include "Tasks.hpp"
#include <stdexcept>
#include <iostream>

#include <nppi_color_conversion.h>

#include <cuda.h>
#include <npp.h>
#include <cuda_runtime.h>

using namespace VPF;

SurfaceFromGL::SurfaceFromGL(uint32_t width, uint32_t height, Pixel_Format format)
    : width(width), height(height), pixelFormat(format) {}

SurfaceFromGL::~SurfaceFromGL() {
    UnregisterTexture();
}

void SurfaceFromGL::RegisterTexture(GLuint texture) {
    if (cudaResource) return;

    auto err = cudaGraphicsGLRegisterImage(
        &cudaResource,
        texture,
        GL_TEXTURE_2D,
        cudaGraphicsRegisterFlagsReadOnly
    );
    if (err != cudaSuccess)
        throw std::runtime_error("cudaGraphicsGLRegisterImage failed");
}

void SurfaceFromGL::UnregisterTexture() {
    if (cudaResource) {
        cudaGraphicsUnregisterResource(cudaResource);
        cudaResource = nullptr;
    }
}

std::shared_ptr<Surface> SurfaceFromGL::ConvertFromTexture(GLuint texture) {

    RegisterTexture(texture);


    if (cudaGraphicsMapResources(1, &cudaResource, 0) != cudaSuccess)
        throw std::runtime_error("cudaGraphicsMapResources failed");

    cudaArray_t array;

    if (cudaGraphicsSubResourceGetMappedArray(&array, cudaResource, 0, 0) != cudaSuccess)
        throw std::runtime_error("cudaGraphicsSubResourceGetMappedArray failed");

    CUcontext cuContext = nullptr;

    if (cuCtxGetCurrent(&cuContext) != CUDA_SUCCESS || cuContext == nullptr)
        throw std::runtime_error("No current CUDA context available");


    auto surfaceRGB = std::make_shared<SurfaceRGB>(width, height, cuContext);
    CUdeviceptr dstPtr = surfaceRGB->PlanePtr();
    size_t dstPitch = surfaceRGB->Pitch();


  
    if (cudaMemcpy2DFromArray(
            (void*)dstPtr,
            dstPitch,
            array,
            0, 0,
            dstPitch,
            height,
            cudaMemcpyDeviceToDevice) != cudaSuccess)
    {
        throw std::runtime_error("cudaMemcpy2DFromArray failed");
    }
    


    cudaGraphicsUnmapResources(1, &cudaResource, 0);

    auto surfaceNV12 = std::make_shared<SurfaceNV12>(width, height, cuContext);

    NppiSize roi = {(int)width, (int)height};
    const Npp8u* pSrc = (const Npp8u*)surfaceRGB->PlanePtr();
    int srcStep = (int)surfaceRGB->Pitch();

    Npp8u* pDstY = (Npp8u*)surfaceNV12->PlanePtr(0);
    Npp8u* pDstUV = (Npp8u*)surfaceNV12->PlanePtr(1);
    int dstPitchY = (int)surfaceNV12->Pitch(0);
    int dstPitchUV = (int)surfaceNV12->Pitch(1);




    NppStreamContext nppCtx = {};
    cudaStream_t stream;
    cudaStreamCreate(&stream);
    nppCtx.hStream = stream;

    cudaDeviceProp prop;
    cudaGetDeviceProperties(&prop, 0);

    nppCtx.nCudaDeviceId = 0;
    nppCtx.nMultiProcessorCount = prop.multiProcessorCount;
    nppCtx.nMaxThreadsPerMultiProcessor = prop.maxThreadsPerMultiProcessor;
    nppCtx.nMaxThreadsPerBlock = prop.maxThreadsPerBlock;
    nppCtx.nSharedMemPerBlock = prop.sharedMemPerBlock;
    nppCtx.nCudaDevAttrComputeCapabilityMajor = prop.major;
    nppCtx.nCudaDevAttrComputeCapabilityMinor = prop.minor;
    nppCtx.nStreamFlags = 0;
    nppCtx.nReserved0 = 0;

 
    const Npp32f twistMatrix[3][4] = {
        { 0.299f,   0.587f,  0.114f,   0.0f }, // Y
        {-0.1687f, -0.3313f, 0.5f,     128.0f }, // U
        { 0.5f,    -0.4187f, -0.0813f, 128.0f }  // V
    };

    Npp8u* pDst[2] = { pDstY, pDstUV };
    int aDstStep[2] = { dstPitchY, dstPitchUV };


    NppStatus err = nppiRGBToNV12_8u_ColorTwist32f_C3P2R_Ctx(
        pSrc,
        srcStep,
        pDst,
        aDstStep,
        roi,
        twistMatrix,
        nppCtx
    );

    if (err != NPP_NO_ERROR) {
        std::cerr << "[ERROR] nppiRGBToNV12_8u_ColorTwist32f_C3P2R_Ctx failed with code: " << err << std::endl;
        throw std::runtime_error("NPP RGB to NV12 conversion failed");
    }


    return surfaceNV12;
}
