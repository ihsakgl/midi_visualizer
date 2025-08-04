#include "bindings.hpp"
#include "surface_to_gpumat.hpp"
#include "VideoFrameProcessor.hpp"
#include "SurfaceFromGL.hpp"

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include <pybind11/chrono.h>
#include <pybind11/pytypes.h>

#include <opencv2/core.hpp>
#include <opencv2/core/cuda.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/imgproc.hpp>

namespace py = pybind11;
using namespace VPF;

void ExportSurfaceToGpuMat(py::module_& m) {
    py::class_<SurfaceToGpuMatConverter, std::shared_ptr<SurfaceToGpuMatConverter>>(m, "SurfaceToGpuMatConverter")
        .def(py::init<std::shared_ptr<VPF::Surface>>())  // Yapıcıyı ekleyin
        .def("get_gpu_mat_ptr", &SurfaceToGpuMatConverter::GetGpuMatPtr)  // GPU matris pointer'ını almak için
        .def("get_width", &SurfaceToGpuMatConverter::GetWidth)
        .def("get_height", &SurfaceToGpuMatConverter::GetHeight)
        .def("get_pitch", &SurfaceToGpuMatConverter::GetPitch)
        .def("get_gpu_mat", &SurfaceToGpuMatConverter::GetGpuMat);  // GetGpuMat fonksiyonunu ekleyin
}


cv::cuda::Stream& getCudaStreamRef(py::object& stream_obj) {
    auto capsule = stream_obj.attr("cudaPtr")();
    void* ptr = reinterpret_cast<void*>(capsule.cast<size_t>());
    return *reinterpret_cast<cv::cuda::Stream*>(ptr);
}

py::array_t<uint8_t> matToNumpy(const cv::Mat& mat) {
    std::vector<size_t> shape = { static_cast<size_t>(mat.rows), static_cast<size_t>(mat.cols), static_cast<size_t>(mat.channels()) };
    std::vector<size_t> strides = { static_cast<size_t>(mat.step[0]), static_cast<size_t>(mat.step[1]), static_cast<size_t>(1) };
    return py::array_t<uint8_t>(shape, strides, mat.data);
}

void ExportVideoFrameProcessor(py::module_& m) {
    py::class_<cv::cuda::Stream>(m, "CudaStream")
        .def(py::init<>())
        .def("wait", &cv::cuda::Stream::waitForCompletion);

    py::class_<VideoFrameProcessor, std::shared_ptr<VideoFrameProcessor>>(m, "VideoFrameProcessor")
        .def(py::init<>())
        .def("update", [](VideoFrameProcessor& self, std::shared_ptr<Surface> surface) {
            self.update(surface);
        })
        .def("crop", [](VideoFrameProcessor& self, int x, int y, int w, int h, cv::cuda::Stream& stream) {
            self.crop(x, y, w, h, stream);
        })
        .def("resize", [](VideoFrameProcessor& self, int w, int h, cv::cuda::Stream& stream) {
            self.resize(w, h, stream);
        })
        .def("scale", [](VideoFrameProcessor& self, double scaleFactor, cv::cuda::Stream& stream) {
            self.scale(scaleFactor, stream);
        })
        .def("rotate", [](VideoFrameProcessor& self, double angle, cv::cuda::Stream& stream) {
            self.rotate(angle, stream);
        })
        .def("rotate_90_ccw", [](VideoFrameProcessor& self, cv::cuda::Stream& stream) {
            self.rotate_90_ccw(stream);
        })
        .def("flip", [](VideoFrameProcessor& self, int flipCode, cv::cuda::Stream& stream) {
            self.flip(flipCode, stream);
        })
        .def("adjustBrightness", [](VideoFrameProcessor& self, float alpha, float beta, cv::cuda::Stream& stream) {
            self.adjustBrightness(alpha, beta, stream);
        })
        .def("convertColor", [](VideoFrameProcessor& self, int code, cv::cuda::Stream& stream) {
            self.convertColor(code, stream);
        })
        .def("download", [](VideoFrameProcessor& self, cv::cuda::Stream& stream) {
            cv::Mat mat = self.download(stream);
            return matToNumpy(mat);
        })
        .def("bind_to_gl_texture", [](VideoFrameProcessor& self, uint32_t texture_id) {
            self.bindToGLTextureOnce(texture_id);
        })
        .def("copy_to_texture", [](VideoFrameProcessor& self) {
            self.copyToTexture();
        })
        .def("set_output_size", [](VideoFrameProcessor& self, int width, int height) {
            self.setOutputSize(width, height);
        });

}

void ExportSurfaceFromGL(py::module_& m) {
    py::class_<SurfaceFromGL>(m, "SurfaceFromGL")
        .def(py::init<uint32_t, uint32_t, Pixel_Format>())
        .def("convert_from_texture", &SurfaceFromGL::ConvertFromTexture);
}