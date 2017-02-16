# Install script for directory: /home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core

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
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkFiltersCore-7.1.so.1"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkFiltersCore-7.1.so"
      )
    IF(EXISTS "${file}" AND
       NOT IS_SYMLINK "${file}")
      FILE(RPATH_CHECK
           FILE "${file}"
           RPATH "")
    ENDIF()
  ENDFOREACH()
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY FILES
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/lib/libvtkFiltersCore-7.1.so.1"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/lib/libvtkFiltersCore-7.1.so"
    )
  FOREACH(file
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkFiltersCore-7.1.so.1"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkFiltersCore-7.1.so"
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
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/vtk-7.1/Modules" TYPE FILE FILES "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/CMakeFiles/vtkFiltersCore.cmake")
ENDIF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")

IF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/vtk-7.1" TYPE FILE FILES
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkAppendFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkAppendPolyData.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkAppendSelection.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkArrayCalculator.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkAssignAttribute.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkAttributeDataToFieldDataFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkBinCellDataFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkCellDataToPointData.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkCleanPolyData.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkClipPolyData.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkCompositeDataProbeFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkConnectivityFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkContourFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkContourGrid.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkContourHelper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkDataObjectGenerator.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkDataObjectToDataSetFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkDataSetEdgeSubdivisionCriterion.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkDataSetToDataObjectFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkDecimatePolylineFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkDecimatePro.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkDelaunay2D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkDelaunay3D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkElevationFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkExecutionTimer.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkFeatureEdges.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkFieldDataToAttributeDataFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkFlyingEdges2D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkFlyingEdges3D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkFlyingEdgesPlaneCutter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkGlyph2D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkGlyph3D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkHedgeHog.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkHull.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkIdFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkMarchingCubes.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkMarchingSquares.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkMaskFields.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkMaskPoints.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkMaskPolyData.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkMassProperties.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkMergeDataObjectFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkMergeFields.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkMergeFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkPointDataToCellData.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkPolyDataConnectivityFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkPolyDataNormals.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkProbeFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkQuadricClustering.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkQuadricDecimation.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkRearrangeFields.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkResampleToImage.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkResampleWithDataSet.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkReverseSense.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkSimpleElevationFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkSmoothPolyDataFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkStripper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkStructuredGridOutlineFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkSynchronizedTemplates2D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkSynchronizedTemplates3D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkSynchronizedTemplatesCutter3D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkTensorGlyph.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkThreshold.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkThresholdPoints.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkTransposeTable.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkTriangleFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkTubeFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkUnstructuredGridQuadricDecimation.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkVectorDot.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkVectorNorm.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkWindowedSincPolyDataFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkCutter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkCompositeCutter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkGridSynchronizedTemplates3D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkRectilinearSynchronizedTemplates.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkEdgeSubdivisionCriterion.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkStreamingTessellator.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkImplicitPolyDataDistance.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkStreamerBase.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkCenterOfMass.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkImageAppend.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkStructuredGridAppend.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkAppendCompositeDataLeaves.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Filters/Core/vtkFiltersCoreModule.h"
    )
ENDIF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")

