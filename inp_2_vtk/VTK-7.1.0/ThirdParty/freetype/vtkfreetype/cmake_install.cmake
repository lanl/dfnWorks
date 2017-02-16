# Install script for directory: /home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype

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
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkfreetype-7.1.so.1"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkfreetype-7.1.so"
      )
    IF(EXISTS "${file}" AND
       NOT IS_SYMLINK "${file}")
      FILE(RPATH_CHECK
           FILE "${file}"
           RPATH "")
    ENDIF()
  ENDFOREACH()
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY FILES
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/lib/libvtkfreetype-7.1.so.1"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/lib/libvtkfreetype-7.1.so"
    )
  FOREACH(file
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkfreetype-7.1.so.1"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkfreetype-7.1.so"
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
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/vtk-7.1/vtkfreetype/include" TYPE FILE FILES
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/ft2build.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/vtk_freetype_mangle.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/vtk_ftmodule.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/vtkFreeTypeConfig.h"
    )
ENDIF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")

IF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/vtk-7.1/vtkfreetype/include/freetype" TYPE FILE FILES
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/freetype.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ftadvanc.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ftbbox.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ftbdf.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ftbitmap.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ftbzip2.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ftcache.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ftchapters.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ftcid.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/fterrdef.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/fterrors.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ftgasp.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ftglyph.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ftgxval.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ftgzip.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ftimage.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ftincrem.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ftlcdfil.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ftlist.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ftlzw.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ftmac.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ftmm.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ftmodapi.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ftmoderr.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ftotval.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ftoutln.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ftpfr.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ftrender.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ftsizes.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ftsnames.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ftstroke.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ftsynth.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ftsystem.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/fttrigon.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/fttypes.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ftwinfnt.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ftxf86.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/t1tables.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ttnameid.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/tttables.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/tttags.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/ttunpat.h"
    )
ENDIF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")

IF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/vtk-7.1/vtkfreetype/include/freetype/config" TYPE FILE FILES
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/config/ftheader.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/config/ftmodule.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/config/ftoption.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/config/ftstdlib.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/freetype/vtkfreetype/include/freetype/config/ftconfig.h"
    )
ENDIF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")

