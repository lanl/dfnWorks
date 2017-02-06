set(vtkIOMINC_HEADERS_LOADED 1)
set(vtkIOMINC_HEADERS "vtkMINCImageAttributes;vtkMINCImageReader;vtkMINCImageWriter;vtkMNIObjectReader;vtkMNIObjectWriter;vtkMNITagPointReader;vtkMNITagPointWriter;vtkMNITransformReader;vtkMNITransformWriter")

foreach(header ${vtkIOMINC_HEADERS})
  set(vtkIOMINC_HEADER_${header}_EXISTS 1)
endforeach()




