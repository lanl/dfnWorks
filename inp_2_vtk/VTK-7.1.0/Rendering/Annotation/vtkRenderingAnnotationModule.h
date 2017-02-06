
#ifndef VTKRENDERINGANNOTATION_EXPORT_H
#define VTKRENDERINGANNOTATION_EXPORT_H

#ifdef VTKRENDERINGANNOTATION_STATIC_DEFINE
#  define VTKRENDERINGANNOTATION_EXPORT
#  define VTKRENDERINGANNOTATION_NO_EXPORT
#else
#  ifndef VTKRENDERINGANNOTATION_EXPORT
#    ifdef vtkRenderingAnnotation_EXPORTS
        /* We are building this library */
#      define VTKRENDERINGANNOTATION_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKRENDERINGANNOTATION_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKRENDERINGANNOTATION_NO_EXPORT
#    define VTKRENDERINGANNOTATION_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKRENDERINGANNOTATION_DEPRECATED
#  define VTKRENDERINGANNOTATION_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKRENDERINGANNOTATION_DEPRECATED_EXPORT VTKRENDERINGANNOTATION_EXPORT __attribute__ ((__deprecated__))
#  define VTKRENDERINGANNOTATION_DEPRECATED_NO_EXPORT VTKRENDERINGANNOTATION_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKRENDERINGANNOTATION_NO_DEPRECATED
#endif

/* AutoInit dependencies.  */
#include "vtkRenderingCoreModule.h"

#endif
