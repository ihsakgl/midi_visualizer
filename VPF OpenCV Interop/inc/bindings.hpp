#ifndef BINDINGS_HPP
#define BINDINGS_HPP

#include <pybind11/pybind11.h>

namespace py = pybind11;

void ExportSurfaceToGpuMat(py::module_& m);

void ExportVideoFrameProcessor(py::module_& m);

void ExportSurfaceFromGL(py::module_& m);

#endif // BINDINGS_HPP