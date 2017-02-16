set(vtkImagingMath_HEADERS_LOADED 1)
set(vtkImagingMath_HEADERS "vtkImageDivergence;vtkImageDotProduct;vtkImageLogarithmicScale;vtkImageLogic;vtkImageMagnitude;vtkImageMaskBits;vtkImageMathematics;vtkImageWeightedSum")

foreach(header ${vtkImagingMath_HEADERS})
  set(vtkImagingMath_HEADER_${header}_EXISTS 1)
endforeach()




