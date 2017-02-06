set(vtkIOXMLParser_HEADERS_LOADED 1)
set(vtkIOXMLParser_HEADERS "vtkXMLDataParser;vtkXMLParser;vtkXMLUtilities")

foreach(header ${vtkIOXMLParser_HEADERS})
  set(vtkIOXMLParser_HEADER_${header}_EXISTS 1)
endforeach()




