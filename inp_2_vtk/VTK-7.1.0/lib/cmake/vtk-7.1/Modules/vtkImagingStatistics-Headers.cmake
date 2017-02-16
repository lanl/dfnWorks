set(vtkImagingStatistics_HEADERS_LOADED 1)
set(vtkImagingStatistics_HEADERS "vtkImageAccumulate;vtkImageHistogram;vtkImageHistogramStatistics")

foreach(header ${vtkImagingStatistics_HEADERS})
  set(vtkImagingStatistics_HEADER_${header}_EXISTS 1)
endforeach()




