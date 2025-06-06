# CMake generated Testfile for 
# Source directory: C:/Users/ihsan/Projects/Synthesia/opencv/opencv/modules/photo
# Build directory: C:/Users/ihsan/Projects/Synthesia/build/modules/photo
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
if(CTEST_CONFIGURATION_TYPE MATCHES "^([Dd][Ee][Bb][Uu][Gg])$")
  add_test([=[opencv_test_photo]=] "C:/Users/ihsan/Projects/Synthesia/build/bin/Debug/opencv_test_photod.exe" "--gtest_output=xml:opencv_test_photo.xml")
  set_tests_properties([=[opencv_test_photo]=] PROPERTIES  LABELS "Main;opencv_photo;Accuracy" WORKING_DIRECTORY "C:/Users/ihsan/Projects/Synthesia/build/test-reports/accuracy" _BACKTRACE_TRIPLES "C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVUtils.cmake;1799;add_test;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVModule.cmake;1365;ocv_add_test_from_target;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVModule.cmake;1123;ocv_add_accuracy_tests;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/modules/photo/CMakeLists.txt;7;ocv_define_module;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/modules/photo/CMakeLists.txt;0;")
elseif(CTEST_CONFIGURATION_TYPE MATCHES "^([Rr][Ee][Ll][Ee][Aa][Ss][Ee])$")
  add_test([=[opencv_test_photo]=] "C:/Users/ihsan/Projects/Synthesia/build/bin/Release/opencv_test_photo.exe" "--gtest_output=xml:opencv_test_photo.xml")
  set_tests_properties([=[opencv_test_photo]=] PROPERTIES  LABELS "Main;opencv_photo;Accuracy" WORKING_DIRECTORY "C:/Users/ihsan/Projects/Synthesia/build/test-reports/accuracy" _BACKTRACE_TRIPLES "C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVUtils.cmake;1799;add_test;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVModule.cmake;1365;ocv_add_test_from_target;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVModule.cmake;1123;ocv_add_accuracy_tests;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/modules/photo/CMakeLists.txt;7;ocv_define_module;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/modules/photo/CMakeLists.txt;0;")
else()
  add_test([=[opencv_test_photo]=] NOT_AVAILABLE)
endif()
if(CTEST_CONFIGURATION_TYPE MATCHES "^([Dd][Ee][Bb][Uu][Gg])$")
  add_test([=[opencv_perf_photo]=] "C:/Users/ihsan/Projects/Synthesia/build/bin/Debug/opencv_perf_photod.exe" "--gtest_output=xml:opencv_perf_photo.xml")
  set_tests_properties([=[opencv_perf_photo]=] PROPERTIES  LABELS "Main;opencv_photo;Performance" WORKING_DIRECTORY "C:/Users/ihsan/Projects/Synthesia/build/test-reports/performance" _BACKTRACE_TRIPLES "C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVUtils.cmake;1799;add_test;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVModule.cmake;1264;ocv_add_test_from_target;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVModule.cmake;1124;ocv_add_perf_tests;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/modules/photo/CMakeLists.txt;7;ocv_define_module;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/modules/photo/CMakeLists.txt;0;")
elseif(CTEST_CONFIGURATION_TYPE MATCHES "^([Rr][Ee][Ll][Ee][Aa][Ss][Ee])$")
  add_test([=[opencv_perf_photo]=] "C:/Users/ihsan/Projects/Synthesia/build/bin/Release/opencv_perf_photo.exe" "--gtest_output=xml:opencv_perf_photo.xml")
  set_tests_properties([=[opencv_perf_photo]=] PROPERTIES  LABELS "Main;opencv_photo;Performance" WORKING_DIRECTORY "C:/Users/ihsan/Projects/Synthesia/build/test-reports/performance" _BACKTRACE_TRIPLES "C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVUtils.cmake;1799;add_test;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVModule.cmake;1264;ocv_add_test_from_target;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVModule.cmake;1124;ocv_add_perf_tests;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/modules/photo/CMakeLists.txt;7;ocv_define_module;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/modules/photo/CMakeLists.txt;0;")
else()
  add_test([=[opencv_perf_photo]=] NOT_AVAILABLE)
endif()
if(CTEST_CONFIGURATION_TYPE MATCHES "^([Dd][Ee][Bb][Uu][Gg])$")
  add_test([=[opencv_sanity_photo]=] "C:/Users/ihsan/Projects/Synthesia/build/bin/Debug/opencv_perf_photod.exe" "--gtest_output=xml:opencv_perf_photo.xml" "--perf_min_samples=1" "--perf_force_samples=1" "--perf_verify_sanity")
  set_tests_properties([=[opencv_sanity_photo]=] PROPERTIES  LABELS "Main;opencv_photo;Sanity" WORKING_DIRECTORY "C:/Users/ihsan/Projects/Synthesia/build/test-reports/sanity" _BACKTRACE_TRIPLES "C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVUtils.cmake;1799;add_test;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVModule.cmake;1265;ocv_add_test_from_target;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVModule.cmake;1124;ocv_add_perf_tests;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/modules/photo/CMakeLists.txt;7;ocv_define_module;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/modules/photo/CMakeLists.txt;0;")
elseif(CTEST_CONFIGURATION_TYPE MATCHES "^([Rr][Ee][Ll][Ee][Aa][Ss][Ee])$")
  add_test([=[opencv_sanity_photo]=] "C:/Users/ihsan/Projects/Synthesia/build/bin/Release/opencv_perf_photo.exe" "--gtest_output=xml:opencv_perf_photo.xml" "--perf_min_samples=1" "--perf_force_samples=1" "--perf_verify_sanity")
  set_tests_properties([=[opencv_sanity_photo]=] PROPERTIES  LABELS "Main;opencv_photo;Sanity" WORKING_DIRECTORY "C:/Users/ihsan/Projects/Synthesia/build/test-reports/sanity" _BACKTRACE_TRIPLES "C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVUtils.cmake;1799;add_test;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVModule.cmake;1265;ocv_add_test_from_target;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVModule.cmake;1124;ocv_add_perf_tests;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/modules/photo/CMakeLists.txt;7;ocv_define_module;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/modules/photo/CMakeLists.txt;0;")
else()
  add_test([=[opencv_sanity_photo]=] NOT_AVAILABLE)
endif()
