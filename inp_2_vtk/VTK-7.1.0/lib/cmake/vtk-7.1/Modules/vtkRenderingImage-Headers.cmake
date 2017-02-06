set(vtkRenderingImage_HEADERS_LOADED 1)
set(vtkRenderingImage_HEADERS "vtkDepthImageToPointCloud;vtkImageResliceMapper;vtkImageSliceCollection;vtkImageStack")

foreach(header ${vtkRenderingImage_HEADERS})
  set(vtkRenderingImage_HEADER_${header}_EXISTS 1)
endforeach()




