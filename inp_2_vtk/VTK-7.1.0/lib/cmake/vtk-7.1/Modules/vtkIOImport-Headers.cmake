set(vtkIOImport_HEADERS_LOADED 1)
set(vtkIOImport_HEADERS "vtk3DSImporter;vtkImporter;vtkVRMLImporter;vtkOBJImporter;vtkOBJImporterInternals")

foreach(header ${vtkIOImport_HEADERS})
  set(vtkIOImport_HEADER_${header}_EXISTS 1)
endforeach()

set(vtkIOImport_HEADER_vtkImporter_ABSTRACT 1)

set(vtkIOImport_HEADER_vtkOBJImporterInternals_WRAP_EXCLUDE 1)

set(vtkIOImport_HEADER_vtkOBJImporterInternals_WRAP_EXCLUDE_PYTHON 1)

