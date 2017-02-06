set(vtkViewsCore_HEADERS_LOADED 1)
set(vtkViewsCore_HEADERS "vtkConvertSelectionDomain;vtkDataRepresentation;vtkEmptyRepresentation;vtkRenderViewBase;vtkView;vtkViewTheme")

foreach(header ${vtkViewsCore_HEADERS})
  set(vtkViewsCore_HEADER_${header}_EXISTS 1)
endforeach()




