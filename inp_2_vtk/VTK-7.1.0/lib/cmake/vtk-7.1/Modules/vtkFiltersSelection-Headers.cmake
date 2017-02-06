set(vtkFiltersSelection_HEADERS_LOADED 1)
set(vtkFiltersSelection_HEADERS "vtkKdTreeSelector;vtkLinearSelector;vtkCellDistanceSelector")

foreach(header ${vtkFiltersSelection_HEADERS})
  set(vtkFiltersSelection_HEADER_${header}_EXISTS 1)
endforeach()




