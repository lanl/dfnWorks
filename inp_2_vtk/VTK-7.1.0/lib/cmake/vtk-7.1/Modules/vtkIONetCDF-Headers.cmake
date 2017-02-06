set(vtkIONetCDF_HEADERS_LOADED 1)
set(vtkIONetCDF_HEADERS "vtkMPASReader;vtkNetCDFCAMReader;vtkNetCDFCFReader;vtkNetCDFPOPReader;vtkNetCDFReader;vtkSLACParticleReader;vtkSLACReader")

foreach(header ${vtkIONetCDF_HEADERS})
  set(vtkIONetCDF_HEADER_${header}_EXISTS 1)
endforeach()




