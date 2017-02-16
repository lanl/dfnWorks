set(vtkFiltersAMR_HEADERS_LOADED 1)
set(vtkFiltersAMR_HEADERS "vtkAMRCutPlane;vtkAMRGaussianPulseSource;vtkAMRResampleFilter;vtkAMRSliceFilter;vtkAMRToMultiBlockFilter;vtkImageToAMR;vtkParallelAMRUtilities")

foreach(header ${vtkFiltersAMR_HEADERS})
  set(vtkFiltersAMR_HEADER_${header}_EXISTS 1)
endforeach()




