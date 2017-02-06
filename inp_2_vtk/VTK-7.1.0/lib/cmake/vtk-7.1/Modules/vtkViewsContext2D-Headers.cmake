set(vtkViewsContext2D_HEADERS_LOADED 1)
set(vtkViewsContext2D_HEADERS "vtkContextView;vtkContextInteractorStyle")

foreach(header ${vtkViewsContext2D_HEADERS})
  set(vtkViewsContext2D_HEADER_${header}_EXISTS 1)
endforeach()




