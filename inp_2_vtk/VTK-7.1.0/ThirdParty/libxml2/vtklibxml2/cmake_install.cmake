# Install script for directory: /home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2

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
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtklibxml2-7.1.so.1"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtklibxml2-7.1.so"
      )
    IF(EXISTS "${file}" AND
       NOT IS_SYMLINK "${file}")
      FILE(RPATH_CHECK
           FILE "${file}"
           RPATH "")
    ENDIF()
  ENDFOREACH()
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY FILES
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/lib/libvtklibxml2-7.1.so.1"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/lib/libvtklibxml2-7.1.so"
    )
  FOREACH(file
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtklibxml2-7.1.so.1"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtklibxml2-7.1.so"
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
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/vtk-7.1/vtklibxml2/libxml" TYPE FILE FILES
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/xmlversion.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/c14n.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/catalog.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/chvalid.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/debugXML.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/dict.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/DOCBparser.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/encoding.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/entities.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/globals.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/hash.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/HTMLparser.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/HTMLtree.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/list.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/nanoftp.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/nanohttp.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/parser.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/parserInternals.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/pattern.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/relaxng.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/SAX.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/SAX2.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/schemasInternals.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/schematron.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/threads.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/tree.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/uri.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/valid.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/vtk_libxml2_mangle.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/xinclude.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/xlink.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/xmlautomata.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/xmlerror.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/xmlexports.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/xmlIO.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/xmlmemory.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/xmlmodule.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/xmlreader.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/xmlregexp.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/xmlsave.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/xmlschemas.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/xmlschemastypes.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/xmlstring.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/xmlunicode.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/xmlwriter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/xpath.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/xpathInternals.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/ThirdParty/libxml2/vtklibxml2/libxml/xpointer.h"
    )
ENDIF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")

