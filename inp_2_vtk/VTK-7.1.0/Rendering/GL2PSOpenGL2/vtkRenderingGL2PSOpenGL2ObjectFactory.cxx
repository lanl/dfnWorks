/*=========================================================================

  Program:   Visualization Toolkit
  Module:    vtkRenderingGL2PSOpenGL2ObjectFactory.cxx

  Copyright (c) Ken Martin, Will Schroeder, Bill Lorensen
  All rights reserved.
  See Copyright.txt or http://www.kitware.com/Copyright.htm for details.

     This software is distributed WITHOUT ANY WARRANTY; without even
     the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
     PURPOSE.  See the above copyright notice for more information.

=========================================================================*/

#include "vtkRenderingGL2PSOpenGL2ObjectFactory.h"
#include "vtkVersion.h"

// Include all of the classes we want to create overrides for.

#include "vtkOpenGLGL2PSHelperImpl.h"

vtkStandardNewMacro(vtkRenderingGL2PSOpenGL2ObjectFactory)

// Now create the functions to create overrides with.

  VTK_CREATE_CREATE_FUNCTION(vtkOpenGLGL2PSHelperImpl)

vtkRenderingGL2PSOpenGL2ObjectFactory::vtkRenderingGL2PSOpenGL2ObjectFactory()
{

    this->RegisterOverride("vtkOpenGLGL2PSHelper",
                           "vtkOpenGLGL2PSHelperImpl",
                           "Override for vtkRenderingGL2PSOpenGL2 module", 1,
                           vtkObjectFactoryCreatevtkOpenGLGL2PSHelperImpl);
}

const char * vtkRenderingGL2PSOpenGL2ObjectFactory::GetVTKSourceVersion()
{
  return VTK_SOURCE_VERSION;
}

void vtkRenderingGL2PSOpenGL2ObjectFactory::PrintSelf(ostream &os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os, indent);
}

// Registration of object factories.
static unsigned int vtkRenderingGL2PSOpenGL2Count;

VTKRENDERINGGL2PSOPENGL2_EXPORT void vtkRenderingGL2PSOpenGL2_AutoInit_Construct()
{
  if(++vtkRenderingGL2PSOpenGL2Count == 1)
    {
    
    vtkRenderingGL2PSOpenGL2ObjectFactory* factory = vtkRenderingGL2PSOpenGL2ObjectFactory::New();
    if (factory)
      {
      // vtkObjectFactory keeps a reference to the "factory",
      vtkObjectFactory::RegisterFactory(factory);
      factory->Delete();
      }
    }
}

VTKRENDERINGGL2PSOPENGL2_EXPORT void vtkRenderingGL2PSOpenGL2_AutoInit_Destruct()
{
  if(--vtkRenderingGL2PSOpenGL2Count == 0)
    {
    // Do not call vtkObjectFactory::UnRegisterFactory because
    // vtkObjectFactory.cxx statically unregisters all factories.
    }
}
