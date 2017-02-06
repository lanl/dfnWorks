
#ifndef VTKINTERACTIONIMAGE_EXPORT_H
#define VTKINTERACTIONIMAGE_EXPORT_H

#ifdef VTKINTERACTIONIMAGE_STATIC_DEFINE
#  define VTKINTERACTIONIMAGE_EXPORT
#  define VTKINTERACTIONIMAGE_NO_EXPORT
#else
#  ifndef VTKINTERACTIONIMAGE_EXPORT
#    ifdef vtkInteractionImage_EXPORTS
        /* We are building this library */
#      define VTKINTERACTIONIMAGE_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKINTERACTIONIMAGE_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKINTERACTIONIMAGE_NO_EXPORT
#    define VTKINTERACTIONIMAGE_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKINTERACTIONIMAGE_DEPRECATED
#  define VTKINTERACTIONIMAGE_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKINTERACTIONIMAGE_DEPRECATED_EXPORT VTKINTERACTIONIMAGE_EXPORT __attribute__ ((__deprecated__))
#  define VTKINTERACTIONIMAGE_DEPRECATED_NO_EXPORT VTKINTERACTIONIMAGE_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKINTERACTIONIMAGE_NO_DEPRECATED
#endif

/* AutoInit dependencies.  */
#include "vtkRenderingCoreModule.h"

#endif
