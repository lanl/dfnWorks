
#ifndef VTKRENDERINGCONTEXTOPENGL2_EXPORT_H
#define VTKRENDERINGCONTEXTOPENGL2_EXPORT_H

#ifdef VTKRENDERINGCONTEXTOPENGL2_STATIC_DEFINE
#  define VTKRENDERINGCONTEXTOPENGL2_EXPORT
#  define VTKRENDERINGCONTEXTOPENGL2_NO_EXPORT
#else
#  ifndef VTKRENDERINGCONTEXTOPENGL2_EXPORT
#    ifdef vtkRenderingContextOpenGL2_EXPORTS
        /* We are building this library */
#      define VTKRENDERINGCONTEXTOPENGL2_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKRENDERINGCONTEXTOPENGL2_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKRENDERINGCONTEXTOPENGL2_NO_EXPORT
#    define VTKRENDERINGCONTEXTOPENGL2_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKRENDERINGCONTEXTOPENGL2_DEPRECATED
#  define VTKRENDERINGCONTEXTOPENGL2_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKRENDERINGCONTEXTOPENGL2_DEPRECATED_EXPORT VTKRENDERINGCONTEXTOPENGL2_EXPORT __attribute__ ((__deprecated__))
#  define VTKRENDERINGCONTEXTOPENGL2_DEPRECATED_NO_EXPORT VTKRENDERINGCONTEXTOPENGL2_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKRENDERINGCONTEXTOPENGL2_NO_DEPRECATED
#endif

/* AutoInit dependencies.  */
#include "vtkRenderingContext2DModule.h"
#include "vtkRenderingContext2DModule.h"
#include "vtkRenderingCoreModule.h"
#include "vtkRenderingFreeTypeModule.h"
#include "vtkRenderingOpenGL2Module.h"

/* AutoInit implementations.  */
#if defined(vtkRenderingContextOpenGL2_INCLUDE)
# include vtkRenderingContextOpenGL2_INCLUDE
#endif
#if defined(vtkRenderingContextOpenGL2_AUTOINIT)
# include "vtkAutoInit.h"
VTK_AUTOINIT(vtkRenderingContextOpenGL2)
#endif

#endif
