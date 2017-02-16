# Install script for directory: /home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core

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
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkRenderingCore-7.1.so.1"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkRenderingCore-7.1.so"
      )
    IF(EXISTS "${file}" AND
       NOT IS_SYMLINK "${file}")
      FILE(RPATH_CHECK
           FILE "${file}"
           RPATH "")
    ENDIF()
  ENDFOREACH()
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY FILES
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/lib/libvtkRenderingCore-7.1.so.1"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/lib/libvtkRenderingCore-7.1.so"
    )
  FOREACH(file
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkRenderingCore-7.1.so.1"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libvtkRenderingCore-7.1.so"
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
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/vtk-7.1/Modules" TYPE FILE FILES "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/CMakeFiles/vtkRenderingCore.cmake")
ENDIF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")

IF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")
  FILE(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/vtk-7.1" TYPE FILE FILES
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkGPUInfoListArray.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkNoise200x200.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkPythagoreanQuadruples.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkRayCastStructures.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkRenderingCoreEnums.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkTDxMotionEventInfo.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkAbstractMapper3D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkAbstractMapper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkAbstractPicker.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkAbstractVolumeMapper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkActor2DCollection.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkActor2D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkActorCollection.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkActor.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkAssembly.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkBackgroundColorMonitor.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkBillboardTextActor3D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkCameraActor.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkCamera.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkCameraInterpolator.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkCellCenterDepthSort.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkColorTransferFunction.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkCompositeDataDisplayAttributes.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkCompositePolyDataMapper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkCoordinate.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkCullerCollection.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkCuller.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkDataSetMapper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkDiscretizableColorTransferFunction.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkDistanceToCamera.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkFollower.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkFrameBufferObjectBase.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkFrustumCoverageCuller.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkFXAAOptions.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkGenericRenderWindowInteractor.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkGenericVertexAttributeMapping.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkGlyph3DMapper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkGPUInfo.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkGPUInfoList.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkGraphicsFactory.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkGraphMapper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkGraphToGlyphs.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkHardwareSelector.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkHierarchicalPolyDataMapper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkImageActor.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkImageMapper3D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkImageMapper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkImageProperty.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkImageSlice.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkImageSliceMapper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkInteractorEventRecorder.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkInteractorObserver.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkLabeledContourMapper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkLightActor.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkLightCollection.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkLight.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkLightKit.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkLogLookupTable.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkLookupTableWithEnabling.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkMapArrayValues.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkMapper2D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkMapperCollection.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkMapper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkObserverMediator.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkPolyDataMapper2D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkPolyDataMapper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkProp3DCollection.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkProp3D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkProp3DFollower.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkPropAssembly.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkPropCollection.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkPropPicker3D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkProp.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkProperty2D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkProperty.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkRendererCollection.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkRenderer.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkRendererDelegate.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkRendererSource.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkRenderPass.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkRenderState.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkRenderWindowCollection.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkRenderWindow.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkRenderWindowInteractor.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkRenderWindowInteractor3D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkSelectVisiblePoints.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkShaderDeviceAdapter2.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkTextActor.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkTextActor3D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkTexture.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkTexturedActor2D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkTransformCoordinateSystems.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkTransformInterpolator.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkTupleInterpolator.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkViewDependentErrorMetric.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkViewport.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkVisibilitySort.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkVolumeCollection.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkVolume.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkVolumeProperty.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkWindowLevelLookupTable.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkWindowToImageFilter.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkAssemblyNode.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkAssemblyPath.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkAssemblyPaths.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkAreaPicker.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkPicker.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkAbstractPropPicker.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkPropPicker.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkPickingManager.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkLODProp3D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkWorldPointPicker.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkCellPicker.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkPointPicker.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkRenderedAreaPicker.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkScenePicker.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkInteractorStyle.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkInteractorStyleSwitchBase.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkInteractorStyle3D.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkTDxInteractorStyle.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkTDxInteractorStyleCamera.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkTDxInteractorStyleSettings.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkStringToImage.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkTextMapper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkTextProperty.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkTextPropertyCollection.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkTextRenderer.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkAbstractInteractionDevice.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkAbstractRenderDevice.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkRenderWidget.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkPointGaussianMapper.h"
    "/home/nknapp/dfnworks-main/inp_2_vtk/VTK-7.1.0/Rendering/Core/vtkRenderingCoreModule.h"
    )
ENDIF(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "Development")

