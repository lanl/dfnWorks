set(vtkImagingColor_HEADERS_LOADED 1)
set(vtkImagingColor_HEADERS "vtkImageHSIToRGB;vtkImageHSVToRGB;vtkImageYIQToRGB;vtkImageLuminance;vtkImageMapToRGBA;vtkImageMapToWindowLevelColors;vtkImageQuantizeRGBToIndex;vtkImageRGBToHSI;vtkImageRGBToHSV;vtkImageRGBToYIQ")

foreach(header ${vtkImagingColor_HEADERS})
  set(vtkImagingColor_HEADER_${header}_EXISTS 1)
endforeach()




