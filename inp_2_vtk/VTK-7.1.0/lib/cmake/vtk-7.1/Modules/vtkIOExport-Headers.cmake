set(vtkIOExport_HEADERS_LOADED 1)
set(vtkIOExport_HEADERS "vtkExporter;vtkGL2PSExporter;vtkIVExporter;vtkOBJExporter;vtkOOGLExporter;vtkPOVExporter;vtkRIBExporter;vtkRIBLight;vtkRIBProperty;vtkVRMLExporter;vtkX3D;vtkX3DExporter;vtkX3DExporterFIWriter;vtkX3DExporterWriter;vtkX3DExporterXMLWriter")

foreach(header ${vtkIOExport_HEADERS})
  set(vtkIOExport_HEADER_${header}_EXISTS 1)
endforeach()

set(vtkIOExport_HEADER_vtkExporter_ABSTRACT 1)

set(vtkIOExport_HEADER_vtkX3D_WRAP_EXCLUDE 1)
set(vtkIOExport_HEADER_vtkX3DExporterFIWriter_WRAP_EXCLUDE 1)
set(vtkIOExport_HEADER_vtkX3DExporterWriter_WRAP_EXCLUDE 1)
set(vtkIOExport_HEADER_vtkX3DExporterXMLWriter_WRAP_EXCLUDE 1)


