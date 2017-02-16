set(vtkIOInfovis_HEADERS_LOADED 1)
set(vtkIOInfovis_HEADERS "vtkBiomTableReader;vtkChacoGraphReader;vtkDelimitedTextReader;vtkDIMACSGraphReader;vtkDIMACSGraphWriter;vtkFixedWidthTextReader;vtkISIReader;vtkMultiNewickTreeReader;vtkNewickTreeReader;vtkNewickTreeWriter;vtkPhyloXMLTreeReader;vtkPhyloXMLTreeWriter;vtkRISReader;vtkTulipReader;vtkXGMLReader;vtkXMLTreeReader")

foreach(header ${vtkIOInfovis_HEADERS})
  set(vtkIOInfovis_HEADER_${header}_EXISTS 1)
endforeach()




