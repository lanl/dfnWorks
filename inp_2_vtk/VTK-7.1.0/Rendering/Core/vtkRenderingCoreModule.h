
#ifndef VTKRENDERINGCORE_EXPORT_H
#define VTKRENDERINGCORE_EXPORT_H

#ifdef VTKRENDERINGCORE_STATIC_DEFINE
#  define VTKRENDERINGCORE_EXPORT
#  define VTKRENDERINGCORE_NO_EXPORT
#else
#  ifndef VTKRENDERINGCORE_EXPORT
#    ifdef vtkRenderingCore_EXPORTS
        /* We are building this library */
#      define VTKRENDERINGCORE_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKRENDERINGCORE_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKRENDERINGCORE_NO_EXPORT
#    define VTKRENDERINGCORE_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKRENDERINGCORE_DEPRECATED
#  define VTKRENDERINGCORE_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKRENDERINGCORE_DEPRECATED_EXPORT VTKRENDERINGCORE_EXPORT __attribute__ ((__deprecated__))
#  define VTKRENDERINGCORE_DEPRECATED_NO_EXPORT VTKRENDERINGCORE_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKRENDERINGCORE_NO_DEPRECATED
#endif

/* AutoInit dependencies.  */
#include "vtkFiltersCoreModule.h"

/* AutoInit implementations.  */
#if defined(vtkRenderingCore_INCLUDE)
# include vtkRenderingCore_INCLUDE
#endif
#if defined(vtkRenderingCore_AUTOINIT)
# include "vtkAutoInit.h"
VTK_AUTOINIT(vtkRenderingCore)
#endif

#endif
