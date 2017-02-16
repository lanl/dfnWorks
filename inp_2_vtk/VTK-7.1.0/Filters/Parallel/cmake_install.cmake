# Install script for directory: /home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel

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
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkFiltersParallel-7.1.so.1"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkFiltersParallel-7.1.so"
      )
    IF(EXISTS "${file}" AND
       NOT IS_SYMLINK "${file}")
      FILE(RPATH_CHECK
           FILE "${file}"
           RPATH "")
    ENDIF()
  ENDFOREACH()
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY FILES
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/lib/libvtkFiltersParallel-7.1.so.1"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/lib/libvtkFiltersParallel-7.1.so"
    )
  FOREACH(file
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkFiltersParallel-7.1.so.1"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkFiltersParallel-7.1.so"
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
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/vtk-7.1/Modules" TYPE FILE FILES "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/CMakeFiles/vtkFiltersParallel.cmake")
ENDIF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")

IF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/vtk-7.1" TYPE FILE FILES
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkAngularPeriodicFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkCollectGraph.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkCollectPolyData.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkCollectTable.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkCutMaterial.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkDuplicatePolyData.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkExtractCTHPart.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkExtractPolyDataPiece.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkExtractUnstructuredGridPiece.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkExtractUserDefinedPiece.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkPCellDataToPointData.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkPExtractArraysOverTime.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkPeriodicFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkPKdTree.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkPLinearExtrusionFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkPMaskPoints.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkPOutlineCornerFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkPOutlineFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkPOutlineFilterInternals.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkPPolyDataNormals.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkPProbeFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkPProjectSphereFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkPReflectionFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkPResampleFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkPSphereSource.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkPYoungsMaterialInterface.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkPassThroughFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkPieceRequestFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkPieceScalars.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkPipelineSize.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkProcessIdScalars.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkRectilinearGridOutlineFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkTransmitPolyDataPiece.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkTransmitStructuredDataPiece.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkTransmitRectilinearGridPiece.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkTransmitStructuredGridPiece.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkTransmitUnstructuredGridPiece.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Parallel/vtkFiltersParallelModule.h"
    )
ENDIF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")

