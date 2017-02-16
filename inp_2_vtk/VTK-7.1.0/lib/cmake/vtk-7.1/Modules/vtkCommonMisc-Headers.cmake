set(vtkCommonMisc_HEADERS_LOADED 1)
set(vtkCommonMisc_HEADERS "vtkContourValues;vtkErrorCode;vtkFunctionParser;vtkHeap;vtkPolygonBuilder")

foreach(header ${vtkCommonMisc_HEADERS})
  set(vtkCommonMisc_HEADER_${header}_EXISTS 1)
endforeach()


set(vtkCommonMisc_HEADER_vtkErrorCode_WRAP_EXCLUDE 1)
set(vtkCommonMisc_HEADER_vtkPolygonBuilder_WRAP_EXCLUDE 1)


