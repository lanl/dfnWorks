set(vtkIOLSDyna_HEADERS_LOADED 1)
set(vtkIOLSDyna_HEADERS "vtkLSDynaPart;vtkLSDynaPartCollection;vtkLSDynaReader;vtkLSDynaSummaryParser")

foreach(header ${vtkIOLSDyna_HEADERS})
  set(vtkIOLSDyna_HEADER_${header}_EXISTS 1)
endforeach()


set(vtkIOLSDyna_HEADER_vtkLSDynaPart_WRAP_EXCLUDE 1)
set(vtkIOLSDyna_HEADER_vtkLSDynaPartCollection_WRAP_EXCLUDE 1)

set(vtkIOLSDyna_HEADER_vtkLSDynaPart_WRAP_EXCLUDE_PYTHON 1)
set(vtkIOLSDyna_HEADER_vtkLSDynaPartCollection_WRAP_EXCLUDE_PYTHON 1)

