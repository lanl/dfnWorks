set(vtkFiltersImaging_HEADERS_LOADED 1)
set(vtkFiltersImaging_HEADERS "vtkPairwiseExtractHistogram2D;vtkExtractHistogram2D;vtkComputeHistogram2DOutliers")

foreach(header ${vtkFiltersImaging_HEADERS})
  set(vtkFiltersImaging_HEADER_${header}_EXISTS 1)
endforeach()




