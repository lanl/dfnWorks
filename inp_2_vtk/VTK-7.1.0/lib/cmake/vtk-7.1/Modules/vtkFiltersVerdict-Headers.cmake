set(vtkFiltersVerdict_HEADERS_LOADED 1)
set(vtkFiltersVerdict_HEADERS "vtkCellQuality;vtkMatrixMathFilter;vtkMeshQuality")

foreach(header ${vtkFiltersVerdict_HEADERS})
  set(vtkFiltersVerdict_HEADER_${header}_EXISTS 1)
endforeach()




