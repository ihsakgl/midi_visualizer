# CMake generated Testfile for 
# Source directory: C:/Users/ihsan/Projects/Synthesia/opencv/opencv/modules/ml
# Build directory: C:/Users/ihsan/Projects/Synthesia/build/modules/ml
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
if(CTEST_CONFIGURATION_TYPE MATCHES "^([Dd][Ee][Bb][Uu][Gg])$")
  add_test([=[opencv_test_ml]=] "C:/Users/ihsan/Projects/Synthesia/build/bin/Debug/opencv_test_mld.exe" "--gtest_output=xml:opencv_test_ml.xml")
  set_tests_properties([=[opencv_test_ml]=] PROPERTIES  LABELS "Main;opencv_ml;Accuracy" WORKING_DIRECTORY "C:/Users/ihsan/Projects/Synthesia/build/test-reports/accuracy" _BACKTRACE_TRIPLES "C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVUtils.cmake;1799;add_test;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVModule.cmake;1365;ocv_add_test_from_target;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVModule.cmake;1123;ocv_add_accuracy_tests;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/modules/ml/CMakeLists.txt;2;ocv_define_module;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/modules/ml/CMakeLists.txt;0;")
elseif(CTEST_CONFIGURATION_TYPE MATCHES "^([Rr][Ee][Ll][Ee][Aa][Ss][Ee])$")
  add_test([=[opencv_test_ml]=] "C:/Users/ihsan/Projects/Synthesia/build/bin/Release/opencv_test_ml.exe" "--gtest_output=xml:opencv_test_ml.xml")
  set_tests_properties([=[opencv_test_ml]=] PROPERTIES  LABELS "Main;opencv_ml;Accuracy" WORKING_DIRECTORY "C:/Users/ihsan/Projects/Synthesia/build/test-reports/accuracy" _BACKTRACE_TRIPLES "C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVUtils.cmake;1799;add_test;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVModule.cmake;1365;ocv_add_test_from_target;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVModule.cmake;1123;ocv_add_accuracy_tests;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/modules/ml/CMakeLists.txt;2;ocv_define_module;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/modules/ml/CMakeLists.txt;0;")
else()
  add_test([=[opencv_test_ml]=] NOT_AVAILABLE)
endif()
