#include "./VTK-7.1.0/IO/Geometry/vtkAVSucdReader.h"
#include "./VTK-7.1.0/Common/Core/vtkNew.h"
#include "./VTK-7.1.0/Common/DataModel/vtkPointData.h"
#include "./VTK-7.1.0/Rendering/Core/vtkProperty.h"
#include "./VTK-7.1.0/Common/DataModel/vtkUnstructuredGrid.h"
#include "vtkUnstructuredGridWriter.h"
#include "vtkShrinkFilter.h"
#include <iostream>
#include <fstream> 

int main(int argc, char* argv[])
{
  if (argc < 3)  {
    std::cerr << "Required parameters: <inp_filename> <vtk_filename>" << std::endl;
    return EXIT_FAILURE;
  }

  std::string inp_filename = argv[1];
  vtkNew<vtkAVSucdReader> reader;
  reader->SetFileName(inp_filename.c_str());
  reader->Update();
  reader->Print(std::cout);
  reader->GetOutput()->Print(std::cout);

  vtkUnstructuredGrid* grid = vtkUnstructuredGrid::SafeDownCast(reader->GetOutput());
  vtkUnstructuredGridWriter* writer = vtkUnstructuredGridWriter::New(); 
  writer->SetInputData(grid);
  writer->SetFileName(argv[2]);
  writer->Write();
  return 0;
}
