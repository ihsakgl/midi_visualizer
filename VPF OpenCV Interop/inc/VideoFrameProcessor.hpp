#pragma once

#include <memory>
#include <opencv2/core/cuda.hpp>
#include <opencv2/cudaimgproc.hpp>
#include <MemoryInterfaces.hpp>
#include <nvcuvid.h>
#include <cuda_gl_interop.h>

namespace VPF {
    class Surface;

    class VideoFrameProcessor {
    public:
        VideoFrameProcessor();
        void update(std::shared_ptr<Surface> surface);
        void crop(int xStart, int xEnd, int yStart, int yEnd, cv::cuda::Stream& stream);
        void resize(int width, int height, cv::cuda::Stream& stream);
        void scale(double scaleFactor, cv::cuda::Stream& stream);
        void rotate(double angle, cv::cuda::Stream& stream);
        void rotate_90_ccw(cv::cuda::Stream& stream);
        void flip(int flipCode, cv::cuda::Stream& stream);
        void adjustBrightness(float alpha, float beta, cv::cuda::Stream& stream);
        void convertColor(int code, cv::cuda::Stream& stream);
        cv::Mat download(cv::cuda::Stream& stream);
        void bindToGLTextureOnce(GLuint texture_id);
        void copyToTexture();
        void setOutputSize(int width, int height);
        cudaGraphicsResource* cuda_resource_ = nullptr;
    private:
        cv::cuda::GpuMat gpu_frame_;
        int output_width_;
        int output_height_;
    };
}