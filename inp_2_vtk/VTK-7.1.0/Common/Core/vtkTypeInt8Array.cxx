/*=========================================================================

  Program:   Visualization Toolkit
  Module:    vtkTypedArray.cxx.in

  Copyright (c) Ken Martin, Will Schroeder, Bill Lorensen
  All rights reserved.
  See Copyright.txt or http://www.kitware.com/Copyright.htm for details.

     This software is distributed WITHOUT ANY WARRANTY; without even
     the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
     PURPOSE.  See the above copyright notice for more information.

=========================================================================*/
#include "vtkTypeInt8Array.h"

#include "vtkObjectFactory.h"

//----------------------------------------------------------------------------
vtkStandardNewMacro(vtkTypeInt8Array);

//----------------------------------------------------------------------------
vtkTypeInt8Array::vtkTypeInt8Array()
{
}

//----------------------------------------------------------------------------
vtkTypeInt8Array::~vtkTypeInt8Array()
{
}

//----------------------------------------------------------------------------
void vtkTypeInt8Array::PrintSelf(ostream& os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os,indent);
}
