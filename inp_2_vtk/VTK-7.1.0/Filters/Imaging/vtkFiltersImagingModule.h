
#ifndef VTKFILTERSIMAGING_EXPORT_H
#define VTKFILTERSIMAGING_EXPORT_H

#ifdef VTKFILTERSIMAGING_STATIC_DEFINE
#  define VTKFILTERSIMAGING_EXPORT
#  define VTKFILTERSIMAGING_NO_EXPORT
#else
#  ifndef VTKFILTERSIMAGING_EXPORT
#    ifdef vtkFiltersImaging_EXPORTS
        /* We are building this library */
#      define VTKFILTERSIMAGING_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKFILTERSIMAGING_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKFILTERSIMAGING_NO_EXPORT
#    define VTKFILTERSIMAGING_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKFILTERSIMAGING_DEPRECATED
#  define VTKFILTERSIMAGING_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKFILTERSIMAGING_DEPRECATED_EXPORT VTKFILTERSIMAGING_EXPORT __attribute__ ((__deprecated__))
#  define VTKFILTERSIMAGING_DEPRECATED_NO_EXPORT VTKFILTERSIMAGING_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKFILTERSIMAGING_NO_DEPRECATED
#endif

/* AutoInit dependencies.  */
#include "vtkFiltersStatisticsModule.h"

#endif
