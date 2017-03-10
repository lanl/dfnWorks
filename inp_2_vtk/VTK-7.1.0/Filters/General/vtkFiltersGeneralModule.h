
#ifndef VTKFILTERSGENERAL_EXPORT_H
#define VTKFILTERSGENERAL_EXPORT_H

#ifdef VTKFILTERSGENERAL_STATIC_DEFINE
#  define VTKFILTERSGENERAL_EXPORT
#  define VTKFILTERSGENERAL_NO_EXPORT
#else
#  ifndef VTKFILTERSGENERAL_EXPORT
#    ifdef vtkFiltersGeneral_EXPORTS
        /* We are building this library */
#      define VTKFILTERSGENERAL_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKFILTERSGENERAL_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKFILTERSGENERAL_NO_EXPORT
#    define VTKFILTERSGENERAL_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKFILTERSGENERAL_DEPRECATED
#  define VTKFILTERSGENERAL_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKFILTERSGENERAL_DEPRECATED_EXPORT VTKFILTERSGENERAL_EXPORT __attribute__ ((__deprecated__))
#  define VTKFILTERSGENERAL_DEPRECATED_NO_EXPORT VTKFILTERSGENERAL_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKFILTERSGENERAL_NO_DEPRECATED
#endif

/* AutoInit dependencies.  */
#include "vtkFiltersCoreModule.h"

#endif
