/*=========================================================================

  Program:   Visualization Toolkit
  Module:    vtkRenderingVolumeOpenGL2ObjectFactory.cxx

  Copyright (c) Ken Martin, Will Schroeder, Bill Lorensen
  All rights reserved.
  See Copyright.txt or http://www.kitware.com/Copyright.htm for details.

     This software is distributed WITHOUT ANY WARRANTY; without even
     the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
     PURPOSE.  See the above copyright notice for more information.

=========================================================================*/

#include "vtkRenderingVolumeOpenGL2ObjectFactory.h"
#include "vtkVersion.h"

// Include all of the classes we want to create overrides for.

#include "vtkOpenGLGPUVolumeRayCastMapper.h"
#include "vtkOpenGLProjectedTetrahedraMapper.h"
#include "vtkOpenGLRayCastImageDisplayHelper.h"

vtkStandardNewMacro(vtkRenderingVolumeOpenGL2ObjectFactory)

// Now create the functions to create overrides with.

  VTK_CREATE_CREATE_FUNCTION(vtkOpenGLGPUVolumeRayCastMapper)
  VTK_CREATE_CREATE_FUNCTION(vtkOpenGLProjectedTetrahedraMapper)
  VTK_CREATE_CREATE_FUNCTION(vtkOpenGLRayCastImageDisplayHelper)

vtkRenderingVolumeOpenGL2ObjectFactory::vtkRenderingVolumeOpenGL2ObjectFactory()
{

    this->RegisterOverride("vtkGPUVolumeRayCastMapper",
                           "vtkOpenGLGPUVolumeRayCastMapper",
                           "Override for vtkRenderingVolumeOpenGL2 module", 1,
                           vtkObjectFactoryCreatevtkOpenGLGPUVolumeRayCastMapper);
    this->RegisterOverride("vtkProjectedTetrahedraMapper",
                           "vtkOpenGLProjectedTetrahedraMapper",
                           "Override for vtkRenderingVolumeOpenGL2 module", 1,
                           vtkObjectFactoryCreatevtkOpenGLProjectedTetrahedraMapper);
    this->RegisterOverride("vtkRayCastImageDisplayHelper",
                           "vtkOpenGLRayCastImageDisplayHelper",
                           "Override for vtkRenderingVolumeOpenGL2 module", 1,
                           vtkObjectFactoryCreatevtkOpenGLRayCastImageDisplayHelper);
}

const char * vtkRenderingVolumeOpenGL2ObjectFactory::GetVTKSourceVersion()
{
  return VTK_SOURCE_VERSION;
}

void vtkRenderingVolumeOpenGL2ObjectFactory::PrintSelf(ostream &os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os, indent);
}

// Registration of object factories.
static unsigned int vtkRenderingVolumeOpenGL2Count;

VTKRENDERINGVOLUMEOPENGL2_EXPORT void vtkRenderingVolumeOpenGL2_AutoInit_Construct()
{
  if(++vtkRenderingVolumeOpenGL2Count == 1)
    {
    
    vtkRenderingVolumeOpenGL2ObjectFactory* factory = vtkRenderingVolumeOpenGL2ObjectFactory::New();
    if (factory)
      {
      // vtkObjectFactory keeps a reference to the "factory",
      vtkObjectFactory::RegisterFactory(factory);
      factory->Delete();
      }
    }
}

VTKRENDERINGVOLUMEOPENGL2_EXPORT void vtkRenderingVolumeOpenGL2_AutoInit_Destruct()
{
  if(--vtkRenderingVolumeOpenGL2Count == 0)
    {
    // Do not call vtkObjectFactory::UnRegisterFactory because
    // vtkObjectFactory.cxx statically unregisters all factories.
    }
}
