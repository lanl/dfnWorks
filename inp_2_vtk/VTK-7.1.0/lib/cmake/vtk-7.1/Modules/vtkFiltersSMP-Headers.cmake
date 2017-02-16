set(vtkFiltersSMP_HEADERS_LOADED 1)
set(vtkFiltersSMP_HEADERS "vtkSMPContourGrid;vtkSMPContourGridManyPieces;vtkSMPMergePoints;vtkSMPMergePolyDataHelper;vtkThreadedSynchronizedTemplates3D;vtkThreadedSynchronizedTemplatesCutter3D;vtkSMPTransform;vtkSMPWarpVector")

foreach(header ${vtkFiltersSMP_HEADERS})
  set(vtkFiltersSMP_HEADER_${header}_EXISTS 1)
endforeach()


set(vtkFiltersSMP_HEADER_vtkSMPMergePolyDataHelper_WRAP_EXCLUDE 1)


