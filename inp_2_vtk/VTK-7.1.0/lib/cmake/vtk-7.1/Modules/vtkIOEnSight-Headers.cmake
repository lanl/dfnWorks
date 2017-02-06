set(vtkIOEnSight_HEADERS_LOADED 1)
set(vtkIOEnSight_HEADERS "vtkEnSight6BinaryReader;vtkEnSight6Reader;vtkEnSightGoldBinaryReader;vtkEnSightGoldReader;vtkEnSightMasterServerReader;vtkEnSightReader;vtkGenericEnSightReader")

foreach(header ${vtkIOEnSight_HEADERS})
  set(vtkIOEnSight_HEADER_${header}_EXISTS 1)
endforeach()

set(vtkIOEnSight_HEADER_vtkEnSightReader_ABSTRACT 1)



