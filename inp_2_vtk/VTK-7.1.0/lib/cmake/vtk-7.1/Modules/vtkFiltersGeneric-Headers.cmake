set(vtkFiltersGeneric_HEADERS_LOADED 1)
set(vtkFiltersGeneric_HEADERS "vtkGenericClip;vtkGenericContourFilter;vtkGenericCutter;vtkGenericDataSetTessellator;vtkGenericGeometryFilter;vtkGenericGlyph3DFilter;vtkGenericOutlineFilter;vtkGenericProbeFilter;vtkGenericStreamTracer")

foreach(header ${vtkFiltersGeneric_HEADERS})
  set(vtkFiltersGeneric_HEADER_${header}_EXISTS 1)
endforeach()




