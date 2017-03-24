
#ifndef VTKIOPARALLEL_EXPORT_H
#define VTKIOPARALLEL_EXPORT_H

#ifdef VTKIOPARALLEL_STATIC_DEFINE
#  define VTKIOPARALLEL_EXPORT
#  define VTKIOPARALLEL_NO_EXPORT
#else
#  ifndef VTKIOPARALLEL_EXPORT
#    ifdef vtkIOParallel_EXPORTS
        /* We are building this library */
#      define VTKIOPARALLEL_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKIOPARALLEL_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKIOPARALLEL_NO_EXPORT
#    define VTKIOPARALLEL_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKIOPARALLEL_DEPRECATED
#  define VTKIOPARALLEL_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKIOPARALLEL_DEPRECATED_EXPORT VTKIOPARALLEL_EXPORT __attribute__ ((__deprecated__))
#  define VTKIOPARALLEL_DEPRECATED_NO_EXPORT VTKIOPARALLEL_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKIOPARALLEL_NO_DEPRECATED
#endif

/* AutoInit dependencies.  */
#include "vtkIOGeometryModule.h"
#include "vtkIOImageModule.h"

/* AutoInit implementations.  */
#if defined(vtkIOParallel_INCLUDE)
# include vtkIOParallel_INCLUDE
#endif
#if defined(vtkIOParallel_AUTOINIT)
# include "vtkAutoInit.h"
VTK_AUTOINIT(vtkIOParallel)
#endif

#endif
