# Install script for directory: /home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core

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
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkInfovisCore-7.1.so.1"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkInfovisCore-7.1.so"
      )
    IF(EXISTS "${file}" AND
       NOT IS_SYMLINK "${file}")
      FILE(RPATH_CHECK
           FILE "${file}"
           RPATH "")
    ENDIF()
  ENDFOREACH()
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY FILES
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/lib/libvtkInfovisCore-7.1.so.1"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/lib/libvtkInfovisCore-7.1.so"
    )
  FOREACH(file
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkInfovisCore-7.1.so.1"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkInfovisCore-7.1.so"
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
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/vtk-7.1/Modules" TYPE FILE FILES "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/CMakeFiles/vtkInfovisCore.cmake")
ENDIF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")

IF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/vtk-7.1" TYPE FILE FILES
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkAddMembershipArray.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkAdjacencyMatrixToEdgeTable.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkArrayNorm.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkArrayToTable.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkCollapseGraph.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkCollapseVerticesByArray.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkDataObjectToTable.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkDotProductSimilarity.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkExtractSelectedTree.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkEdgeCenters.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkExpandSelectedGraph.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkExtractSelectedGraph.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkGenerateIndexArray.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkGraphHierarchicalBundleEdges.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkGroupLeafVertices.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkMergeColumns.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkMergeGraphs.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkMergeTables.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkMutableGraphHelper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkNetworkHierarchy.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkPipelineGraphSource.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkPruneTreeFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkRandomGraphSource.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkReduceTable.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkRemoveIsolatedVertices.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkSparseArrayToTable.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkStreamGraph.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkStringToCategory.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkStringToNumeric.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkTableToArray.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkTableToGraph.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkTableToSparseArray.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkTableToTreeFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkThresholdGraph.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkThresholdTable.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkTransferAttributes.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkTransposeMatrix.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkTreeFieldAggregator.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkTreeDifferenceFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkTreeLevelsFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkVertexDegree.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkRemoveHiddenData.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkKCoreDecomposition.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Infovis/Core/vtkInfovisCoreModule.h"
    )
ENDIF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")

