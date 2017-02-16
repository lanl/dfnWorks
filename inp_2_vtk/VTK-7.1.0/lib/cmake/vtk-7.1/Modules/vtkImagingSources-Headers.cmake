set(vtkImagingSources_HEADERS_LOADED 1)
set(vtkImagingSources_HEADERS "vtkImageCanvasSource2D;vtkImageEllipsoidSource;vtkImageGaussianSource;vtkImageGridSource;vtkImageMandelbrotSource;vtkImageNoiseSource;vtkImageSinusoidSource")

foreach(header ${vtkImagingSources_HEADERS})
  set(vtkImagingSources_HEADER_${header}_EXISTS 1)
endforeach()




