
#ifndef VTKRENDERINGVOLUMEOPENGL2_EXPORT_H
#define VTKRENDERINGVOLUMEOPENGL2_EXPORT_H

#ifdef VTKRENDERINGVOLUMEOPENGL2_STATIC_DEFINE
#  define VTKRENDERINGVOLUMEOPENGL2_EXPORT
#  define VTKRENDERINGVOLUMEOPENGL2_NO_EXPORT
#else
#  ifndef VTKRENDERINGVOLUMEOPENGL2_EXPORT
#    ifdef vtkRenderingVolumeOpenGL2_EXPORTS
        /* We are building this library */
#      define VTKRENDERINGVOLUMEOPENGL2_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKRENDERINGVOLUMEOPENGL2_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKRENDERINGVOLUMEOPENGL2_NO_EXPORT
#    define VTKRENDERINGVOLUMEOPENGL2_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKRENDERINGVOLUMEOPENGL2_DEPRECATED
#  define VTKRENDERINGVOLUMEOPENGL2_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKRENDERINGVOLUMEOPENGL2_DEPRECATED_EXPORT VTKRENDERINGVOLUMEOPENGL2_EXPORT __attribute__ ((__deprecated__))
#  define VTKRENDERINGVOLUMEOPENGL2_DEPRECATED_NO_EXPORT VTKRENDERINGVOLUMEOPENGL2_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKRENDERINGVOLUMEOPENGL2_NO_DEPRECATED
#endif

/* AutoInit dependencies.  */
#include "vtkRenderingCoreModule.h"
#include "vtkRenderingOpenGL2Module.h"
#include "vtkRenderingVolumeModule.h"
#include "vtkRenderingVolumeModule.h"

/* AutoInit implementations.  */
#if defined(vtkRenderingVolumeOpenGL2_INCLUDE)
# include vtkRenderingVolumeOpenGL2_INCLUDE
#endif
#if defined(vtkRenderingVolumeOpenGL2_AUTOINIT)
# include "vtkAutoInit.h"
VTK_AUTOINIT(vtkRenderingVolumeOpenGL2)
#endif

#endif
