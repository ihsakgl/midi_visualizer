# Install script for directory: C:/Users/ihsan/Projects/Synthesia/VideoProcessingFramework/src/PyNvCodec

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "C:/Program Files/PyNvCodec")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Release")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("C:/Users/ihsan/Projects/Synthesia/VPF_build/_deps/pybind11-build/cmake_install.cmake")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Dd][Ee][Bb][Uu][Gg])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/PyNvCodec" TYPE MODULE FILES "C:/Users/ihsan/Projects/Synthesia/VPF_build/src/PyNvCodec/Debug/_PyNvCodec.cp312-win_amd64.pyd")
  elseif(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Rr][Ee][Ll][Ee][Aa][Ss][Ee])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/PyNvCodec" TYPE MODULE FILES "C:/Users/ihsan/Projects/Synthesia/VPF_build/src/PyNvCodec/Release/_PyNvCodec.cp312-win_amd64.pyd")
  elseif(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Mm][Ii][Nn][Ss][Ii][Zz][Ee][Rr][Ee][Ll])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/PyNvCodec" TYPE MODULE FILES "C:/Users/ihsan/Projects/Synthesia/VPF_build/src/PyNvCodec/MinSizeRel/_PyNvCodec.cp312-win_amd64.pyd")
  elseif(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Rr][Ee][Ll][Ww][Ii][Tt][Hh][Dd][Ee][Bb][Ii][Nn][Ff][Oo])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/PyNvCodec" TYPE MODULE FILES "C:/Users/ihsan/Projects/Synthesia/VPF_build/src/PyNvCodec/RelWithDebInfo/_PyNvCodec.cp312-win_amd64.pyd")
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Dd][Ee][Bb][Uu][Gg])$")
    file(GET_RUNTIME_DEPENDENCIES
      RESOLVED_DEPENDENCIES_VAR _CMAKE_DEPS
      MODULES
        "C:/Users/ihsan/Projects/Synthesia/VPF_build/src/PyNvCodec/Debug/_PyNvCodec.cp312-win_amd64.pyd"
      DIRECTORIES
        "C:/libs/FFmpeg/bin/"
        "C:/libs/FFmpeg/lib/"
        "C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.8/bin"
        "C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.8/lib/x64"
      PRE_EXCLUDE_REGEXES
        "api-ms-"
        "ext-ms-"
        "python"
        "nvcuda"
      POST_EXCLUDE_REGEXES
        ".*system32/.*\\.dll"
      )
  elseif(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Rr][Ee][Ll][Ee][Aa][Ss][Ee])$")
    file(GET_RUNTIME_DEPENDENCIES
      RESOLVED_DEPENDENCIES_VAR _CMAKE_DEPS
      MODULES
        "C:/Users/ihsan/Projects/Synthesia/VPF_build/src/PyNvCodec/Release/_PyNvCodec.cp312-win_amd64.pyd"
      DIRECTORIES
        "C:/libs/FFmpeg/bin/"
        "C:/libs/FFmpeg/lib/"
        "C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.8/bin"
        "C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.8/lib/x64"
      PRE_EXCLUDE_REGEXES
        "api-ms-"
        "ext-ms-"
        "python"
        "nvcuda"
      POST_EXCLUDE_REGEXES
        ".*system32/.*\\.dll"
      )
  elseif(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Mm][Ii][Nn][Ss][Ii][Zz][Ee][Rr][Ee][Ll])$")
    file(GET_RUNTIME_DEPENDENCIES
      RESOLVED_DEPENDENCIES_VAR _CMAKE_DEPS
      MODULES
        "C:/Users/ihsan/Projects/Synthesia/VPF_build/src/PyNvCodec/MinSizeRel/_PyNvCodec.cp312-win_amd64.pyd"
      DIRECTORIES
        "C:/libs/FFmpeg/bin/"
        "C:/libs/FFmpeg/lib/"
        "C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.8/bin"
        "C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.8/lib/x64"
      PRE_EXCLUDE_REGEXES
        "api-ms-"
        "ext-ms-"
        "python"
        "nvcuda"
      POST_EXCLUDE_REGEXES
        ".*system32/.*\\.dll"
      )
  elseif(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Rr][Ee][Ll][Ww][Ii][Tt][Hh][Dd][Ee][Bb][Ii][Nn][Ff][Oo])$")
    file(GET_RUNTIME_DEPENDENCIES
      RESOLVED_DEPENDENCIES_VAR _CMAKE_DEPS
      MODULES
        "C:/Users/ihsan/Projects/Synthesia/VPF_build/src/PyNvCodec/RelWithDebInfo/_PyNvCodec.cp312-win_amd64.pyd"
      DIRECTORIES
        "C:/libs/FFmpeg/bin/"
        "C:/libs/FFmpeg/lib/"
        "C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.8/bin"
        "C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.8/lib/x64"
      PRE_EXCLUDE_REGEXES
        "api-ms-"
        "ext-ms-"
        "python"
        "nvcuda"
      POST_EXCLUDE_REGEXES
        ".*system32/.*\\.dll"
      )
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Dd][Ee][Bb][Uu][Gg])$")
    foreach(_CMAKE_TMP_dep IN LISTS _CMAKE_DEPS)
      file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/PyNvCodec" TYPE SHARED_LIBRARY FILES ${_CMAKE_TMP_dep}
        FOLLOW_SYMLINK_CHAIN)
    endforeach()
  elseif(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Rr][Ee][Ll][Ee][Aa][Ss][Ee])$")
    foreach(_CMAKE_TMP_dep IN LISTS _CMAKE_DEPS)
      file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/PyNvCodec" TYPE SHARED_LIBRARY FILES ${_CMAKE_TMP_dep}
        FOLLOW_SYMLINK_CHAIN)
    endforeach()
  elseif(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Mm][Ii][Nn][Ss][Ii][Zz][Ee][Rr][Ee][Ll])$")
    foreach(_CMAKE_TMP_dep IN LISTS _CMAKE_DEPS)
      file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/PyNvCodec" TYPE SHARED_LIBRARY FILES ${_CMAKE_TMP_dep}
        FOLLOW_SYMLINK_CHAIN)
    endforeach()
  elseif(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Rr][Ee][Ll][Ww][Ii][Tt][Hh][Dd][Ee][Bb][Ii][Nn][Ff][Oo])$")
    foreach(_CMAKE_TMP_dep IN LISTS _CMAKE_DEPS)
      file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/PyNvCodec" TYPE SHARED_LIBRARY FILES ${_CMAKE_TMP_dep}
        FOLLOW_SYMLINK_CHAIN)
    endforeach()
  endif()
endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
if(CMAKE_INSTALL_LOCAL_ONLY)
  file(WRITE "C:/Users/ihsan/Projects/Synthesia/VPF_build/src/PyNvCodec/install_local_manifest.txt"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
endif()
