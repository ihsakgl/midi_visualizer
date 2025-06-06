# CMake generated Testfile for 
# Source directory: C:/Users/ihsan/Projects/Synthesia/opencv/opencv/modules/core
# Build directory: C:/Users/ihsan/Projects/Synthesia/build/modules/core
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
if(CTEST_CONFIGURATION_TYPE MATCHES "^([Dd][Ee][Bb][Uu][Gg])$")
  add_test([=[opencv_test_core]=] "C:/Users/ihsan/Projects/Synthesia/build/bin/Debug/opencv_test_cored.exe" "--gtest_output=xml:opencv_test_core.xml")
  set_tests_properties([=[opencv_test_core]=] PROPERTIES  LABELS "Main;opencv_core;Accuracy" WORKING_DIRECTORY "C:/Users/ihsan/Projects/Synthesia/build/test-reports/accuracy" _BACKTRACE_TRIPLES "C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVUtils.cmake;1799;add_test;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVModule.cmake;1365;ocv_add_test_from_target;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/modules/core/CMakeLists.txt;212;ocv_add_accuracy_tests;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/modules/core/CMakeLists.txt;0;")
elseif(CTEST_CONFIGURATION_TYPE MATCHES "^([Rr][Ee][Ll][Ee][Aa][Ss][Ee])$")
  add_test([=[opencv_test_core]=] "C:/Users/ihsan/Projects/Synthesia/build/bin/Release/opencv_test_core.exe" "--gtest_output=xml:opencv_test_core.xml")
  set_tests_properties([=[opencv_test_core]=] PROPERTIES  LABELS "Main;opencv_core;Accuracy" WORKING_DIRECTORY "C:/Users/ihsan/Projects/Synthesia/build/test-reports/accuracy" _BACKTRACE_TRIPLES "C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVUtils.cmake;1799;add_test;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVModule.cmake;1365;ocv_add_test_from_target;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/modules/core/CMakeLists.txt;212;ocv_add_accuracy_tests;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/modules/core/CMakeLists.txt;0;")
else()
  add_test([=[opencv_test_core]=] NOT_AVAILABLE)
endif()
if(CTEST_CONFIGURATION_TYPE MATCHES "^([Dd][Ee][Bb][Uu][Gg])$")
  add_test([=[opencv_perf_core]=] "C:/Users/ihsan/Projects/Synthesia/build/bin/Debug/opencv_perf_cored.exe" "--gtest_output=xml:opencv_perf_core.xml")
  set_tests_properties([=[opencv_perf_core]=] PROPERTIES  LABELS "Main;opencv_core;Performance" WORKING_DIRECTORY "C:/Users/ihsan/Projects/Synthesia/build/test-reports/performance" _BACKTRACE_TRIPLES "C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVUtils.cmake;1799;add_test;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVModule.cmake;1264;ocv_add_test_from_target;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/modules/core/CMakeLists.txt;213;ocv_add_perf_tests;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/modules/core/CMakeLists.txt;0;")
elseif(CTEST_CONFIGURATION_TYPE MATCHES "^([Rr][Ee][Ll][Ee][Aa][Ss][Ee])$")
  add_test([=[opencv_perf_core]=] "C:/Users/ihsan/Projects/Synthesia/build/bin/Release/opencv_perf_core.exe" "--gtest_output=xml:opencv_perf_core.xml")
  set_tests_properties([=[opencv_perf_core]=] PROPERTIES  LABELS "Main;opencv_core;Performance" WORKING_DIRECTORY "C:/Users/ihsan/Projects/Synthesia/build/test-reports/performance" _BACKTRACE_TRIPLES "C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVUtils.cmake;1799;add_test;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVModule.cmake;1264;ocv_add_test_from_target;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/modules/core/CMakeLists.txt;213;ocv_add_perf_tests;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/modules/core/CMakeLists.txt;0;")
else()
  add_test([=[opencv_perf_core]=] NOT_AVAILABLE)
endif()
if(CTEST_CONFIGURATION_TYPE MATCHES "^([Dd][Ee][Bb][Uu][Gg])$")
  add_test([=[opencv_sanity_core]=] "C:/Users/ihsan/Projects/Synthesia/build/bin/Debug/opencv_perf_cored.exe" "--gtest_output=xml:opencv_perf_core.xml" "--perf_min_samples=1" "--perf_force_samples=1" "--perf_verify_sanity")
  set_tests_properties([=[opencv_sanity_core]=] PROPERTIES  LABELS "Main;opencv_core;Sanity" WORKING_DIRECTORY "C:/Users/ihsan/Projects/Synthesia/build/test-reports/sanity" _BACKTRACE_TRIPLES "C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVUtils.cmake;1799;add_test;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVModule.cmake;1265;ocv_add_test_from_target;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/modules/core/CMakeLists.txt;213;ocv_add_perf_tests;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/modules/core/CMakeLists.txt;0;")
elseif(CTEST_CONFIGURATION_TYPE MATCHES "^([Rr][Ee][Ll][Ee][Aa][Ss][Ee])$")
  add_test([=[opencv_sanity_core]=] "C:/Users/ihsan/Projects/Synthesia/build/bin/Release/opencv_perf_core.exe" "--gtest_output=xml:opencv_perf_core.xml" "--perf_min_samples=1" "--perf_force_samples=1" "--perf_verify_sanity")
  set_tests_properties([=[opencv_sanity_core]=] PROPERTIES  LABELS "Main;opencv_core;Sanity" WORKING_DIRECTORY "C:/Users/ihsan/Projects/Synthesia/build/test-reports/sanity" _BACKTRACE_TRIPLES "C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVUtils.cmake;1799;add_test;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/cmake/OpenCVModule.cmake;1265;ocv_add_test_from_target;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/modules/core/CMakeLists.txt;213;ocv_add_perf_tests;C:/Users/ihsan/Projects/Synthesia/opencv/opencv/modules/core/CMakeLists.txt;0;")
else()
  add_test([=[opencv_sanity_core]=] NOT_AVAILABLE)
endif()
