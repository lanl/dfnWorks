#include "./VTK-7.1.0/IO/Geometry/vtkAVSucdReader.h"
#include "./VTK-7.1.0/Common/Core/vtkNew.h"
#include "./VTK-7.1.0/Common/DataModel/vtkPointData.h"
#include "./VTK-7.1.0/Rendering/Core/vtkProperty.h"
#include "./VTK-7.1.0/Common/DataModel/vtkUnstructuredGrid.h"
#include "vtkUnstructuredGridWriter.h"
#include "vtkAppendFilter.h"
#include "vtkDataObjectReader.h"
#include <iostream>
#include <fstream> 

int main(int argc, char* argv[])
{
  if (argc < 4)  {
    std::cerr << "Required parameters: <inp_filename> <pflotran_output_directory> <vtk_filename>" << std::endl;
    return EXIT_FAILURE;
  }

  // Read in the inp / AVS file to a vtkUnstructuredGrid data object
  vtkNew<vtkAVSucdReader> inp_reader;
  inp_reader->SetFileName(argv[1]);
  inp_reader->Update();
  vtkUnstructuredGrid* grid = vtkUnstructuredGrid::SafeDownCast(inp_reader->GetOutput());
 
  // Read in the pflotran output info - point data containg cell permeability and pressure
  vtkNew<vtkDataObjectReader> pflotran_reader;  
  pflotran_reader->SetFileName(argv[2]);
  pflotran_reader->Update();
  vtkUnstructuredGrid* pflotran_grid = vtkUnstructuredGrid::SafeDownCast(pflotran_reader->GetOutput());
  
  // Combine the grids
  vtkNew<vtkAppendFilter> append_filter;
  append_filter->AddInputData(grid);
  append_filter->AddInputData(pflotran_grid);
  append_filter->Update();  
  vtkUnstructuredGrid* end_grid = append_filter->GetOutput();

  // Write the vtkUnstructuredGrid into a VTK file 
  vtkUnstructuredGridWriter* writer = vtkUnstructuredGridWriter::New(); 
  writer->SetInputData(end_grid);
  writer->SetFileName(argv[3]);
  writer->Write();
  return 0;
}
