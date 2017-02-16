
#ifndef VTKIOGEOMETRY_EXPORT_H
#define VTKIOGEOMETRY_EXPORT_H

#ifdef VTKIOGEOMETRY_STATIC_DEFINE
#  define VTKIOGEOMETRY_EXPORT
#  define VTKIOGEOMETRY_NO_EXPORT
#else
#  ifndef VTKIOGEOMETRY_EXPORT
#    ifdef vtkIOGeometry_EXPORTS
        /* We are building this library */
#      define VTKIOGEOMETRY_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKIOGEOMETRY_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKIOGEOMETRY_NO_EXPORT
#    define VTKIOGEOMETRY_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKIOGEOMETRY_DEPRECATED
#  define VTKIOGEOMETRY_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKIOGEOMETRY_DEPRECATED_EXPORT VTKIOGEOMETRY_EXPORT __attribute__ ((__deprecated__))
#  define VTKIOGEOMETRY_DEPRECATED_NO_EXPORT VTKIOGEOMETRY_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKIOGEOMETRY_NO_DEPRECATED
#endif

/* AutoInit implementations.  */
#if defined(vtkIOGeometry_INCLUDE)
# include vtkIOGeometry_INCLUDE
#endif
#if defined(vtkIOGeometry_AUTOINIT)
# include "vtkAutoInit.h"
VTK_AUTOINIT(vtkIOGeometry)
#endif

#endif
