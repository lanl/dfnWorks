# Install script for directory: /home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/IO/Geometry

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
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkIOGeometry-7.1.so.1"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkIOGeometry-7.1.so"
      )
    IF(EXISTS "${file}" AND
       NOT IS_SYMLINK "${file}")
      FILE(RPATH_CHECK
           FILE "${file}"
           RPATH "")
    ENDIF()
  ENDFOREACH()
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY FILES
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/lib/libvtkIOGeometry-7.1.so.1"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/lib/libvtkIOGeometry-7.1.so"
    )
  FOREACH(file
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkIOGeometry-7.1.so.1"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkIOGeometry-7.1.so"
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
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/vtk-7.1/Modules" TYPE FILE FILES "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/IO/Geometry/CMakeFiles/vtkIOGeometry.cmake")
ENDIF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")

IF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/vtk-7.1" TYPE FILE FILES
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/IO/Geometry/vtkAVSucdReader.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/IO/Geometry/vtkBYUReader.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/IO/Geometry/vtkBYUWriter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/IO/Geometry/vtkChacoReader.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/IO/Geometry/vtkFacetWriter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/IO/Geometry/vtkFLUENTReader.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/IO/Geometry/vtkGAMBITReader.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/IO/Geometry/vtkGaussianCubeReader.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/IO/Geometry/vtkHoudiniPolyDataWriter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/IO/Geometry/vtkIVWriter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/IO/Geometry/vtkMCubesReader.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/IO/Geometry/vtkMCubesWriter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/IO/Geometry/vtkMFIXReader.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/IO/Geometry/vtkMoleculeReaderBase.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/IO/Geometry/vtkOBJReader.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/IO/Geometry/vtkOpenFOAMReader.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/IO/Geometry/vtkParticleReader.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/IO/Geometry/vtkPDBReader.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/IO/Geometry/vtkProStarReader.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/IO/Geometry/vtkPTSReader.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/IO/Geometry/vtkSTLReader.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/IO/Geometry/vtkSTLWriter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/IO/Geometry/vtkTecplotReader.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/IO/Geometry/vtkUGFacetReader.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/IO/Geometry/vtkWindBladeReader.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/IO/Geometry/vtkXYZMolReader.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/IO/Geometry/vtkIOGeometryModule.h"
    )
ENDIF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")

