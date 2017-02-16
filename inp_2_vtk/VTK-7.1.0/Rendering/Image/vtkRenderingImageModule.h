
#ifndef VTKRENDERINGIMAGE_EXPORT_H
#define VTKRENDERINGIMAGE_EXPORT_H

#ifdef VTKRENDERINGIMAGE_STATIC_DEFINE
#  define VTKRENDERINGIMAGE_EXPORT
#  define VTKRENDERINGIMAGE_NO_EXPORT
#else
#  ifndef VTKRENDERINGIMAGE_EXPORT
#    ifdef vtkRenderingImage_EXPORTS
        /* We are building this library */
#      define VTKRENDERINGIMAGE_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKRENDERINGIMAGE_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKRENDERINGIMAGE_NO_EXPORT
#    define VTKRENDERINGIMAGE_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKRENDERINGIMAGE_DEPRECATED
#  define VTKRENDERINGIMAGE_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKRENDERINGIMAGE_DEPRECATED_EXPORT VTKRENDERINGIMAGE_EXPORT __attribute__ ((__deprecated__))
#  define VTKRENDERINGIMAGE_DEPRECATED_NO_EXPORT VTKRENDERINGIMAGE_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKRENDERINGIMAGE_NO_DEPRECATED
#endif

/* AutoInit dependencies.  */
#include "vtkRenderingCoreModule.h"

#endif
