/*=========================================================================

  Program:   Visualization Toolkit
  Module:    vtkRenderingFreeTypeObjectFactory.cxx

  Copyright (c) Ken Martin, Will Schroeder, Bill Lorensen
  All rights reserved.
  See Copyright.txt or http://www.kitware.com/Copyright.htm for details.

     This software is distributed WITHOUT ANY WARRANTY; without even
     the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
     PURPOSE.  See the above copyright notice for more information.

=========================================================================*/

#include "vtkRenderingFreeTypeObjectFactory.h"
#include "vtkVersion.h"

// Include all of the classes we want to create overrides for.

#include "vtkMathTextFreeTypeTextRenderer.h"

vtkStandardNewMacro(vtkRenderingFreeTypeObjectFactory)

// Now create the functions to create overrides with.

  VTK_CREATE_CREATE_FUNCTION(vtkMathTextFreeTypeTextRenderer)

vtkRenderingFreeTypeObjectFactory::vtkRenderingFreeTypeObjectFactory()
{

    this->RegisterOverride("vtkTextRenderer",
                           "vtkMathTextFreeTypeTextRenderer",
                           "Override for vtkRenderingFreeType module", 1,
                           vtkObjectFactoryCreatevtkMathTextFreeTypeTextRenderer);
}

const char * vtkRenderingFreeTypeObjectFactory::GetVTKSourceVersion()
{
  return VTK_SOURCE_VERSION;
}

void vtkRenderingFreeTypeObjectFactory::PrintSelf(ostream &os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os, indent);
}

// Registration of object factories.
static unsigned int vtkRenderingFreeTypeCount;

VTKRENDERINGFREETYPE_EXPORT void vtkRenderingFreeType_AutoInit_Construct()
{
  if(++vtkRenderingFreeTypeCount == 1)
    {
    
    vtkRenderingFreeTypeObjectFactory* factory = vtkRenderingFreeTypeObjectFactory::New();
    if (factory)
      {
      // vtkObjectFactory keeps a reference to the "factory",
      vtkObjectFactory::RegisterFactory(factory);
      factory->Delete();
      }
    }
}

VTKRENDERINGFREETYPE_EXPORT void vtkRenderingFreeType_AutoInit_Destruct()
{
  if(--vtkRenderingFreeTypeCount == 0)
    {
    // Do not call vtkObjectFactory::UnRegisterFactory because
    // vtkObjectFactory.cxx statically unregisters all factories.
    }
}
