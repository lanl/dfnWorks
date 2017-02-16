set(vtkImagingFourier_HEADERS_LOADED 1)
set(vtkImagingFourier_HEADERS "vtkImageButterworthHighPass;vtkImageButterworthLowPass;vtkImageFFT;vtkImageFourierCenter;vtkImageFourierFilter;vtkImageIdealHighPass;vtkImageIdealLowPass;vtkImageRFFT;vtkTableFFT")

foreach(header ${vtkImagingFourier_HEADERS})
  set(vtkImagingFourier_HEADER_${header}_EXISTS 1)
endforeach()

set(vtkImagingFourier_HEADER_vtkImageFourierFilter_ABSTRACT 1)



