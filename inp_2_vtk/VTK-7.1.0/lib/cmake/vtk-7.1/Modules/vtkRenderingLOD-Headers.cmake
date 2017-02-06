set(vtkRenderingLOD_HEADERS_LOADED 1)
set(vtkRenderingLOD_HEADERS "vtkLODActor;vtkQuadricLODActor")

foreach(header ${vtkRenderingLOD_HEADERS})
  set(vtkRenderingLOD_HEADER_${header}_EXISTS 1)
endforeach()




