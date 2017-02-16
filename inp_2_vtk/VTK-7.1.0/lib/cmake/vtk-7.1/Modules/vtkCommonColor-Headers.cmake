set(vtkCommonColor_HEADERS_LOADED 1)
set(vtkCommonColor_HEADERS "vtkColorSeries;vtkNamedColors")

foreach(header ${vtkCommonColor_HEADERS})
  set(vtkCommonColor_HEADER_${header}_EXISTS 1)
endforeach()




