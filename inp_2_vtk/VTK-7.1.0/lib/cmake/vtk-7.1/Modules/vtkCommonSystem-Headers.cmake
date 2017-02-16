set(vtkCommonSystem_HEADERS_LOADED 1)
set(vtkCommonSystem_HEADERS "vtkClientSocket;vtkDirectory;vtkServerSocket;vtkSocket;vtkSocketCollection;vtkThreadMessager;vtkTimerLog")

foreach(header ${vtkCommonSystem_HEADERS})
  set(vtkCommonSystem_HEADER_${header}_EXISTS 1)
endforeach()

set(vtkCommonSystem_HEADER_vtkSocket_ABSTRACT 1)



