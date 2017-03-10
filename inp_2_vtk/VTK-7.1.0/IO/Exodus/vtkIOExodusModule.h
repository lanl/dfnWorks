
#ifndef VTKIOEXODUS_EXPORT_H
#define VTKIOEXODUS_EXPORT_H

#ifdef VTKIOEXODUS_STATIC_DEFINE
#  define VTKIOEXODUS_EXPORT
#  define VTKIOEXODUS_NO_EXPORT
#else
#  ifndef VTKIOEXODUS_EXPORT
#    ifdef vtkIOExodus_EXPORTS
        /* We are building this library */
#      define VTKIOEXODUS_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKIOEXODUS_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKIOEXODUS_NO_EXPORT
#    define VTKIOEXODUS_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKIOEXODUS_DEPRECATED
#  define VTKIOEXODUS_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKIOEXODUS_DEPRECATED_EXPORT VTKIOEXODUS_EXPORT __attribute__ ((__deprecated__))
#  define VTKIOEXODUS_DEPRECATED_NO_EXPORT VTKIOEXODUS_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKIOEXODUS_NO_DEPRECATED
#endif

/* AutoInit implementations.  */
#if defined(vtkIOExodus_INCLUDE)
# include vtkIOExodus_INCLUDE
#endif
#if defined(vtkIOExodus_AUTOINIT)
# include "vtkAutoInit.h"
VTK_AUTOINIT(vtkIOExodus)
#endif

#endif
