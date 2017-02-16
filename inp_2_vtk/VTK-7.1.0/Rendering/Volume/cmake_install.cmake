# Install script for directory: /home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume

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
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkRenderingVolume-7.1.so.1"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkRenderingVolume-7.1.so"
      )
    IF(EXISTS "${file}" AND
       NOT IS_SYMLINK "${file}")
      FILE(RPATH_CHECK
           FILE "${file}"
           RPATH "")
    ENDIF()
  ENDFOREACH()
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY FILES
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/lib/libvtkRenderingVolume-7.1.so.1"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/lib/libvtkRenderingVolume-7.1.so"
    )
  FOREACH(file
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkRenderingVolume-7.1.so.1"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkRenderingVolume-7.1.so"
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
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/vtk-7.1/Modules" TYPE FILE FILES "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/CMakeFiles/vtkRenderingVolume.cmake")
ENDIF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")

IF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/vtk-7.1" TYPE FILE FILES
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkDirectionEncoder.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkEncodedGradientEstimator.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkEncodedGradientShader.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkFiniteDifferenceGradientEstimator.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkFixedPointRayCastImage.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkFixedPointVolumeRayCastCompositeGOHelper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkFixedPointVolumeRayCastCompositeGOShadeHelper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkFixedPointVolumeRayCastCompositeHelper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkFixedPointVolumeRayCastCompositeShadeHelper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkFixedPointVolumeRayCastHelper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkFixedPointVolumeRayCastMIPHelper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkFixedPointVolumeRayCastMapper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkGPUVolumeRayCastMapper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkOSPRayVolumeInterface.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkProjectedTetrahedraMapper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkRayCastImageDisplayHelper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkRecursiveSphereDirectionEncoder.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkSphericalDirectionEncoder.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkUnstructuredGridBunykRayCastFunction.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkUnstructuredGridHomogeneousRayIntegrator.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkUnstructuredGridLinearRayIntegrator.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkUnstructuredGridPartialPreIntegration.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkUnstructuredGridPreIntegration.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkUnstructuredGridVolumeMapper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkUnstructuredGridVolumeRayCastFunction.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkUnstructuredGridVolumeRayCastIterator.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkUnstructuredGridVolumeRayCastMapper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkUnstructuredGridVolumeRayIntegrator.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkUnstructuredGridVolumeZSweepMapper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkVolumeMapper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkVolumeOutlineSource.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkVolumePicker.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkVolumeRayCastCompositeFunction.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkVolumeRayCastFunction.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkVolumeRayCastIsosurfaceFunction.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkVolumeRayCastMIPFunction.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkVolumeRayCastMapper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkVolumeRayCastSpaceLeapingImageFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Volume/vtkRenderingVolumeModule.h"
    )
ENDIF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")

