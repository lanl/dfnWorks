
#ifndef VTKFILTERSPARALLELIMAGING_EXPORT_H
#define VTKFILTERSPARALLELIMAGING_EXPORT_H

#ifdef VTKFILTERSPARALLELIMAGING_STATIC_DEFINE
#  define VTKFILTERSPARALLELIMAGING_EXPORT
#  define VTKFILTERSPARALLELIMAGING_NO_EXPORT
#else
#  ifndef VTKFILTERSPARALLELIMAGING_EXPORT
#    ifdef vtkFiltersParallelImaging_EXPORTS
        /* We are building this library */
#      define VTKFILTERSPARALLELIMAGING_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKFILTERSPARALLELIMAGING_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKFILTERSPARALLELIMAGING_NO_EXPORT
#    define VTKFILTERSPARALLELIMAGING_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKFILTERSPARALLELIMAGING_DEPRECATED
#  define VTKFILTERSPARALLELIMAGING_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKFILTERSPARALLELIMAGING_DEPRECATED_EXPORT VTKFILTERSPARALLELIMAGING_EXPORT __attribute__ ((__deprecated__))
#  define VTKFILTERSPARALLELIMAGING_DEPRECATED_NO_EXPORT VTKFILTERSPARALLELIMAGING_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKFILTERSPARALLELIMAGING_NO_DEPRECATED
#endif

/* AutoInit dependencies.  */
#include "vtkFiltersImagingModule.h"
#include "vtkFiltersParallelModule.h"

#endif
