
#ifndef VTKRENDERINGOPENGL2_EXPORT_H
#define VTKRENDERINGOPENGL2_EXPORT_H

#ifdef VTKRENDERINGOPENGL2_STATIC_DEFINE
#  define VTKRENDERINGOPENGL2_EXPORT
#  define VTKRENDERINGOPENGL2_NO_EXPORT
#else
#  ifndef VTKRENDERINGOPENGL2_EXPORT
#    ifdef vtkRenderingOpenGL2_EXPORTS
        /* We are building this library */
#      define VTKRENDERINGOPENGL2_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKRENDERINGOPENGL2_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKRENDERINGOPENGL2_NO_EXPORT
#    define VTKRENDERINGOPENGL2_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKRENDERINGOPENGL2_DEPRECATED
#  define VTKRENDERINGOPENGL2_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKRENDERINGOPENGL2_DEPRECATED_EXPORT VTKRENDERINGOPENGL2_EXPORT __attribute__ ((__deprecated__))
#  define VTKRENDERINGOPENGL2_DEPRECATED_NO_EXPORT VTKRENDERINGOPENGL2_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKRENDERINGOPENGL2_NO_DEPRECATED
#endif

#include "vtkRenderingOpenGLConfigure.h"

/* AutoInit dependencies.  */
#include "vtkRenderingCoreModule.h"
#include "vtkRenderingCoreModule.h"

/* AutoInit implementations.  */
#if defined(vtkRenderingOpenGL2_INCLUDE)
# include vtkRenderingOpenGL2_INCLUDE
#endif
#if defined(vtkRenderingOpenGL2_AUTOINIT)
# include "vtkAutoInit.h"
VTK_AUTOINIT(vtkRenderingOpenGL2)
#endif

#endif
