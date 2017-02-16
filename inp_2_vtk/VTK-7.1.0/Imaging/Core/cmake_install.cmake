# Install script for directory: /home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core

# Set the install prefix
IF(NOT DEFINED CMAKE_INSTALL_PREFIX)
  SET(CMAKE_INSTALL_PREFIX "/usr/local")
ENDIF(NOT DEFINED CMAKE_INSTALL_PREFIX)
STRING(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
IF(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  IF(BUILD_TYPE)
    STRING(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  ELSE(BUILD_TYPE)
    SET(CMAKE_INSTALL_CONFIG_NAME "Debug")
  ENDIF(BUILD_TYPE)
  MESSAGE(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
ENDIF(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)

# Set the component getting installed.
IF(NOT CMAKE_INSTALL_COMPONENT)
  IF(COMPONENT)
    MESSAGE(STATUS "Install component: \"${COMPONENT}\"")
    SET(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  ELSE(COMPONENT)
    SET(CMAKE_INSTALL_COMPONENT)
  ENDIF(COMPONENT)
ENDIF(NOT CMAKE_INSTALL_COMPONENT)

# Install shared libraries without execute permission?
IF(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  SET(CMAKE_INSTALL_SO_NO_EXE "1")
ENDIF(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)

IF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "RuntimeLibraries")
  FOREACH(file
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkImagingCore-7.1.so.1"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkImagingCore-7.1.so"
      )
    IF(EXISTS "${file}" AND
       NOT IS_SYMLINK "${file}")
      FILE(RPATH_CHECK
           FILE "${file}"
           RPATH "")
    ENDIF()
  ENDFOREACH()
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY FILES
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/lib/libvtkImagingCore-7.1.so.1"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/lib/libvtkImagingCore-7.1.so"
    )
  FOREACH(file
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkImagingCore-7.1.so.1"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkImagingCore-7.1.so"
      )
    IF(EXISTS "${file}" AND
       NOT IS_SYMLINK "${file}")
      FILE(RPATH_REMOVE
           FILE "${file}")
      IF(CMAKE_INSTALL_DO_STRIP)
        EXECUTE_PROCESS(COMMAND "/usr/bin/strip" "${file}")
      ENDIF(CMAKE_INSTALL_DO_STRIP)
    ENDIF()
  ENDFOREACH()
ENDIF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "RuntimeLibraries")

IF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/vtk-7.1/Modules" TYPE FILE FILES "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/CMakeFiles/vtkImagingCore.cmake")
ENDIF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")

IF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/vtk-7.1" TYPE FILE FILES
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkExtractVOI.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageAppendComponents.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageBlend.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageCacheFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageCast.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageChangeInformation.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageClip.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageConstantPad.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageDataStreamer.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageDecomposeFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageDifference.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageExtractComponents.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageFlip.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageIterateFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageMagnify.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageMapToColors.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageMask.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageMirrorPad.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImagePadFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImagePermute.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImagePointDataIterator.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImagePointIterator.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageResample.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageReslice.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageResliceToColors.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageShiftScale.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageShrink3D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageStencilIterator.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageThreshold.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageTranslateExtent.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageWrapPad.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkRTAnalyticSource.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageResize.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageBSplineCoefficients.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageStencilData.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageStencilAlgorithm.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkAbstractImageInterpolator.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageBSplineInternals.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageBSplineInterpolator.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageSincInterpolator.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageInterpolator.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImageStencilSource.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Imaging/Core/vtkImagingCoreModule.h"
    )
ENDIF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")

