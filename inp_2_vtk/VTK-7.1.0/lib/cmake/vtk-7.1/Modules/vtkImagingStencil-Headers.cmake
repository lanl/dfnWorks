set(vtkImagingStencil_HEADERS_LOADED 1)
set(vtkImagingStencil_HEADERS "vtkImageStencil;vtkImageStencilToImage;vtkImageToImageStencil;vtkImplicitFunctionToImageStencil;vtkLassoStencilSource;vtkPolyDataToImageStencil;vtkROIStencilSource")

foreach(header ${vtkImagingStencil_HEADERS})
  set(vtkImagingStencil_HEADER_${header}_EXISTS 1)
endforeach()




