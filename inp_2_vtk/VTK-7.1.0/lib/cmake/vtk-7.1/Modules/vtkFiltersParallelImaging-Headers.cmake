set(vtkFiltersParallelImaging_HEADERS_LOADED 1)
set(vtkFiltersParallelImaging_HEADERS "vtkPComputeHistogram2DOutliers;vtkPExtractHistogram2D;vtkPPairwiseExtractHistogram2D;vtkExtractPiece;vtkMemoryLimitImageDataStreamer;vtkTransmitImageDataPiece")

foreach(header ${vtkFiltersParallelImaging_HEADERS})
  set(vtkFiltersParallelImaging_HEADER_${header}_EXISTS 1)
endforeach()




