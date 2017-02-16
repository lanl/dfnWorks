# Install script for directory: /home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2

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
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkRenderingOpenGL2-7.1.so.1"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkRenderingOpenGL2-7.1.so"
      )
    IF(EXISTS "${file}" AND
       NOT IS_SYMLINK "${file}")
      FILE(RPATH_CHECK
           FILE "${file}"
           RPATH "")
    ENDIF()
  ENDFOREACH()
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY FILES
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/lib/libvtkRenderingOpenGL2-7.1.so.1"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/lib/libvtkRenderingOpenGL2-7.1.so"
    )
  FOREACH(file
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkRenderingOpenGL2-7.1.so.1"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkRenderingOpenGL2-7.1.so"
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
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/vtk-7.1/Modules" TYPE FILE FILES "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/CMakeFiles/vtkRenderingOpenGL2.cmake")
ENDIF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")

IF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/vtk-7.1" TYPE FILE FILES
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGL.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkTDxConfigure.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLError.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkRenderingOpenGLConfigure.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkRenderingOpenGL2ObjectFactory.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkCameraPass.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkClearRGBPass.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkClearZPass.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkCompositePolyDataMapper2.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkDefaultPass.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkDepthOfFieldPass.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkDepthImageProcessingPass.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkDepthPeelingPass.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkEDLShading.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkFrameBufferObject.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkGaussianBlurPass.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkGenericOpenGLRenderWindow.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkHiddenLineRemovalPass.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkImageProcessingPass.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkLightingMapPass.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkLightsPass.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpaquePass.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLActor.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLBillboardTextActor3D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLBufferObject.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLCamera.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLFXAAFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLGL2PSHelper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLGlyph3DHelper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLGlyph3DMapper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLHardwareSelector.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLHelper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLImageAlgorithmHelper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLImageMapper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLImageSliceMapper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLIndexBufferObject.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLLabeledContourMapper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLLight.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLPointGaussianMapper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLPolyDataMapper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLPolyDataMapper2D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLProperty.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLRenderPass.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLRenderTimer.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLRenderUtilities.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLRenderWindow.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLRenderer.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLShaderCache.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLSphereMapper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLStickMapper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLTextActor.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLTextActor3D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLTextMapper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLTexture.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLVertexArrayObject.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOpenGLVertexBufferObject.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkOverlayPass.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkPointFillPass.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkRenderPassCollection.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkRenderStepsPass.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkSSAAPass.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkSequencePass.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkShader.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkShaderProgram.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkShadowMapBakerPass.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkShadowMapPass.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkSobelGradientMagnitudePass.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkTextureObject.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkTextureUnitManager.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkTransformFeedback.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkTranslucentPass.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkVolumetricPass.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkDataTransferHelper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkDualDepthPeelingPass.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkFrameBufferObject2.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkPixelBufferObject.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkRenderbuffer.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkValuePass.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkValuePassHelper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkDummyGPUInfoList.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkXRenderWindowInteractor.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkXOpenGLRenderWindow.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/OpenGL2/vtkRenderingOpenGL2Module.h"
    )
ENDIF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")

