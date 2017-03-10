/*=========================================================================

  Program:   Visualization Toolkit
  Module:    vtkRenderingContextOpenGL2ObjectFactory.cxx

  Copyright (c) Ken Martin, Will Schroeder, Bill Lorensen
  All rights reserved.
  See Copyright.txt or http://www.kitware.com/Copyright.htm for details.

     This software is distributed WITHOUT ANY WARRANTY; without even
     the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
     PURPOSE.  See the above copyright notice for more information.

=========================================================================*/

#include "vtkRenderingContextOpenGL2ObjectFactory.h"
#include "vtkVersion.h"

// Include all of the classes we want to create overrides for.

#include "vtkOpenGLContextActor.h"
#include "vtkOpenGLContextDevice2D.h"
#include "vtkOpenGLContextDevice3D.h"
#include "vtkOpenGLPropItem.h"
#include "vtkOpenGLContextBufferId.h"

vtkStandardNewMacro(vtkRenderingContextOpenGL2ObjectFactory)

// Now create the functions to create overrides with.

  VTK_CREATE_CREATE_FUNCTION(vtkOpenGLContextActor)
  VTK_CREATE_CREATE_FUNCTION(vtkOpenGLContextDevice2D)
  VTK_CREATE_CREATE_FUNCTION(vtkOpenGLContextDevice3D)
  VTK_CREATE_CREATE_FUNCTION(vtkOpenGLPropItem)
  VTK_CREATE_CREATE_FUNCTION(vtkOpenGLContextBufferId)

vtkRenderingContextOpenGL2ObjectFactory::vtkRenderingContextOpenGL2ObjectFactory()
{

    this->RegisterOverride("vtkContextActor",
                           "vtkOpenGLContextActor",
                           "Override for vtkRenderingContextOpenGL2 module", 1,
                           vtkObjectFactoryCreatevtkOpenGLContextActor);
    this->RegisterOverride("vtkContextDevice2D",
                           "vtkOpenGLContextDevice2D",
                           "Override for vtkRenderingContextOpenGL2 module", 1,
                           vtkObjectFactoryCreatevtkOpenGLContextDevice2D);
    this->RegisterOverride("vtkContextDevice3D",
                           "vtkOpenGLContextDevice3D",
                           "Override for vtkRenderingContextOpenGL2 module", 1,
                           vtkObjectFactoryCreatevtkOpenGLContextDevice3D);
    this->RegisterOverride("vtkPropItem",
                           "vtkOpenGLPropItem",
                           "Override for vtkRenderingContextOpenGL2 module", 1,
                           vtkObjectFactoryCreatevtkOpenGLPropItem);
    this->RegisterOverride("vtkAbstractContextBufferId",
                           "vtkOpenGLContextBufferId",
                           "Override for vtkRenderingContextOpenGL2 module", 1,
                           vtkObjectFactoryCreatevtkOpenGLContextBufferId);
}

const char * vtkRenderingContextOpenGL2ObjectFactory::GetVTKSourceVersion()
{
  return VTK_SOURCE_VERSION;
}

void vtkRenderingContextOpenGL2ObjectFactory::PrintSelf(ostream &os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os, indent);
}

// Registration of object factories.
static unsigned int vtkRenderingContextOpenGL2Count;

VTKRENDERINGCONTEXTOPENGL2_EXPORT void vtkRenderingContextOpenGL2_AutoInit_Construct()
{
  if(++vtkRenderingContextOpenGL2Count == 1)
    {
    
    vtkRenderingContextOpenGL2ObjectFactory* factory = vtkRenderingContextOpenGL2ObjectFactory::New();
    if (factory)
      {
      // vtkObjectFactory keeps a reference to the "factory",
      vtkObjectFactory::RegisterFactory(factory);
      factory->Delete();
      }
    }
}

VTKRENDERINGCONTEXTOPENGL2_EXPORT void vtkRenderingContextOpenGL2_AutoInit_Destruct()
{
  if(--vtkRenderingContextOpenGL2Count == 0)
    {
    // Do not call vtkObjectFactory::UnRegisterFactory because
    // vtkObjectFactory.cxx statically unregisters all factories.
    }
}
