set(vtkImagingHybrid_HEADERS_LOADED 1)
set(vtkImagingHybrid_HEADERS "vtkBooleanTexture;vtkCheckerboardSplatter;vtkFastSplatter;vtkGaussianSplatter;vtkImageCursor3D;vtkImageRectilinearWipe;vtkImageToPoints;vtkPointLoad;vtkSampleFunction;vtkShepardMethod;vtkSliceCubes;vtkSurfaceReconstructionFilter;vtkTriangularTexture;vtkVoxelModeller")

foreach(header ${vtkImagingHybrid_HEADERS})
  set(vtkImagingHybrid_HEADER_${header}_EXISTS 1)
endforeach()




