# Install script for directory: /home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Context2D

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
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkRenderingContext2D-7.1.so.1"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkRenderingContext2D-7.1.so"
      )
    IF(EXISTS "${file}" AND
       NOT IS_SYMLINK "${file}")
      FILE(RPATH_CHECK
           FILE "${file}"
           RPATH "")
    ENDIF()
  ENDFOREACH()
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY FILES
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/lib/libvtkRenderingContext2D-7.1.so.1"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/lib/libvtkRenderingContext2D-7.1.so"
    )
  FOREACH(file
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkRenderingContext2D-7.1.so.1"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkRenderingContext2D-7.1.so"
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
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/vtk-7.1/Modules" TYPE FILE FILES "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Context2D/CMakeFiles/vtkRenderingContext2D.cmake")
ENDIF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")

IF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/vtk-7.1" TYPE FILE FILES
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Context2D/vtkAbstractContextBufferId.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Context2D/vtkAbstractContextItem.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Context2D/vtkBlockItem.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Context2D/vtkBrush.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Context2D/vtkContext2D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Context2D/vtkContext3D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Context2D/vtkContextActor.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Context2D/vtkContextClip.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Context2D/vtkContextDevice2D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Context2D/vtkContextDevice3D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Context2D/vtkContextItem.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Context2D/vtkContextKeyEvent.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Context2D/vtkContextMapper2D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Context2D/vtkContextMouseEvent.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Context2D/vtkContextScene.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Context2D/vtkContextTransform.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Context2D/vtkImageItem.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Context2D/vtkMarkerUtilities.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Context2D/vtkPen.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Context2D/vtkPropItem.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Context2D/vtkTooltipItem.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Context2D/vtkRenderingContext2DModule.h"
    )
ENDIF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")

