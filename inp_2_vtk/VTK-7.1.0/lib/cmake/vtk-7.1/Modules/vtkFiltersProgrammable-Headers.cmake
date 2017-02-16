set(vtkFiltersProgrammable_HEADERS_LOADED 1)
set(vtkFiltersProgrammable_HEADERS "vtkProgrammableAttributeDataFilter;vtkProgrammableFilter;vtkProgrammableGlyphFilter")

foreach(header ${vtkFiltersProgrammable_HEADERS})
  set(vtkFiltersProgrammable_HEADER_${header}_EXISTS 1)
endforeach()




