set(vtkInteractionImage_HEADERS_LOADED 1)
set(vtkInteractionImage_HEADERS "vtkImageViewer2;vtkImageViewer;vtkResliceImageViewer;vtkResliceImageViewerMeasurements")

foreach(header ${vtkInteractionImage_HEADERS})
  set(vtkInteractionImage_HEADER_${header}_EXISTS 1)
endforeach()




