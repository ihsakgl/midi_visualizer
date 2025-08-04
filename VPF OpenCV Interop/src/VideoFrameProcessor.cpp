#include "VideoFrameProcessor.hpp"
#include <opencv2/imgproc.hpp>
#include <cudawarping.hpp>
#include <cudaarithm.hpp>
#include <MemoryInterfaces.hpp>
#include <iostream>
#include <cuda_runtime_api.h>
#include <cuda_gl_interop.h>



using namespace VPF;

VideoFrameProcessor::VideoFrameProcessor() {
  
    cv::cuda::GpuMat gpu_frame_;
    cudaGraphicsResource* cuda_resource_ = nullptr;
    int output_width_ = -1;
    int output_height_ = -1;

}

void VideoFrameProcessor::update(std::shared_ptr<Surface> surface) {
    SurfacePlane* plane = surface->GetSurfacePlane(0);
    if (!plane || plane->GpuMem() == 0) {
        throw std::runtime_error("Invalid surface.");
    }

    gpu_frame_ = cv::cuda::GpuMat(
        plane->Height(),          
        plane->Width() / 3,       
        CV_8UC3,                  
        reinterpret_cast<void*>(plane->GpuMem()),
        plane->Pitch()           
    );
}


void VideoFrameProcessor::crop(int xStart, int xEnd, int yStart, int yEnd, cv::cuda::Stream& stream) {
    gpu_frame_ = gpu_frame_.colRange(xStart, xEnd);
    gpu_frame_ = gpu_frame_.rowRange(yStart, yEnd);  
}

void VideoFrameProcessor::resize(int width, int height, cv::cuda::Stream& stream) {
    cv::cuda::GpuMat out;
    cv::cuda::resize(gpu_frame_, out, cv::Size(width, height), 0, 0, cv::INTER_LINEAR, stream);
    gpu_frame_ = out;
}

void VideoFrameProcessor::scale(double scaleFactor, cv::cuda::Stream& stream) {
    cv::cuda::GpuMat out;
    cv::cuda::resize(gpu_frame_, out, cv::Size (0, 0), scaleFactor, scaleFactor, cv::INTER_LINEAR, stream);
    gpu_frame_ = out;
}

void VideoFrameProcessor::rotate(double angle, cv::cuda::Stream& stream) {
    
    auto center = cv::Point2f(gpu_frame_.cols / 2.0f, gpu_frame_.rows / 2.0f);
    cv::Mat rot_mat = cv::getRotationMatrix2D(center, angle, 1.0);
  
    

    cv::cuda::GpuMat out;
    cv::cuda::warpAffine(gpu_frame_, out, rot_mat, gpu_frame_.size(), cv::INTER_LINEAR, cv::BORDER_CONSTANT, cv::Scalar(), stream);
    gpu_frame_ = out;
  
    
}

void VideoFrameProcessor::rotate_90_ccw(cv::cuda::Stream& stream) {
   
    cv::cuda::GpuMat channels[3];  // RGBA için 4 kanal
    cv::cuda::split(gpu_frame_, channels, stream);
    

    // Her bir kanalı transpose + flip et
    for (int i = 0; i < 3; ++i) {
        cv::cuda::GpuMat temp;
        cv::cuda::transpose(channels[i], temp, stream);
        cv::cuda::flip(temp, channels[i], 0, stream);
    }

    cv::cuda::merge(channels, 3, gpu_frame_, stream);
    
   
}


void VideoFrameProcessor::flip(int flipCode, cv::cuda::Stream& stream) {
    cv::cuda::GpuMat out;
    cv::cuda::flip(gpu_frame_, out, flipCode, stream);
    gpu_frame_ = out;
}

void VideoFrameProcessor::adjustBrightness(float alpha, float beta, cv::cuda::Stream& stream) {
    cv::cuda::GpuMat temp;
    cv::cuda::multiply(gpu_frame_, cv::Scalar::all(alpha), temp, 1.0, -1, stream);
    cv::cuda::add(temp, cv::Scalar::all(beta), gpu_frame_, cv::noArray(), -1, stream);
    
}

void VideoFrameProcessor::convertColor(int code, cv::cuda::Stream& stream) {
    cv::cuda::GpuMat out;
    cv::cuda::cvtColor(gpu_frame_, out, code, 0, stream);
    gpu_frame_ = out;
}

cv::Mat VideoFrameProcessor::download(cv::cuda::Stream& stream) {
    cv::Mat frame;
    gpu_frame_.download(frame, stream);
    return frame;
}

void VideoFrameProcessor::bindToGLTextureOnce(GLuint texture_id) {
    if (!cuda_resource_) {
        cudaError_t err = cudaGraphicsGLRegisterImage(
            &cuda_resource_,
            texture_id,
            GL_TEXTURE_2D,
            cudaGraphicsRegisterFlagsWriteDiscard
        );
        if (err != cudaSuccess) {
            throw std::runtime_error("cudaGraphicsGLRegisterImage failed");
        }
    }
}

void VideoFrameProcessor::copyToTexture() {
    if (!cuda_resource_) return;

    cudaGraphicsMapResources(1, &cuda_resource_, 0);
    cudaArray_t texture_array;
    cudaGraphicsSubResourceGetMappedArray(&texture_array, cuda_resource_, 0, 0);

    
    //std::cout << "Rows: " << gpu_frame_.rows << std::endl;
    //std::cout << "Cols: " << gpu_frame_.cols << std::endl;
    //std::cout << "spitch: " << gpu_frame_.step << std::endl;
    


    cudaError_t err = cudaMemcpy2DToArray(
        texture_array,
        0, 0,
        gpu_frame_.ptr<void>(),
        gpu_frame_.step,
        gpu_frame_.cols * gpu_frame_.elemSize(),
        gpu_frame_.rows,
        cudaMemcpyDeviceToDevice
    );

    if (err != cudaSuccess) {
        std::cerr << "cudaMemcpy2DToArray failed: " << cudaGetErrorString(err) << std::endl;
    }

    cudaGraphicsUnmapResources(1, &cuda_resource_, 0);
}

void VideoFrameProcessor::setOutputSize(int width, int height) {
    output_width_ = width;
    output_height_ = height;
}

/*
void VideoFrameProcessor::bindToGLTextureOnce(GLuint texture_id) {
    if (!cuda_resource_) {
        cudaError_t err = cudaGraphicsGLRegisterImage(
            &cuda_resource_,
            texture_id,
            GL_TEXTURE_2D,
            cudaGraphicsRegisterFlagsWriteDiscard
        );
        if (err != cudaSuccess) {
            throw std::runtime_error("cudaGraphicsGLRegisterImage failed");
        }
    }
}
*/