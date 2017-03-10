
#ifndef VTKFILTERSPARALLEL_EXPORT_H
#define VTKFILTERSPARALLEL_EXPORT_H

#ifdef VTKFILTERSPARALLEL_STATIC_DEFINE
#  define VTKFILTERSPARALLEL_EXPORT
#  define VTKFILTERSPARALLEL_NO_EXPORT
#else
#  ifndef VTKFILTERSPARALLEL_EXPORT
#    ifdef vtkFiltersParallel_EXPORTS
        /* We are building this library */
#      define VTKFILTERSPARALLEL_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKFILTERSPARALLEL_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKFILTERSPARALLEL_NO_EXPORT
#    define VTKFILTERSPARALLEL_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKFILTERSPARALLEL_DEPRECATED
#  define VTKFILTERSPARALLEL_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKFILTERSPARALLEL_DEPRECATED_EXPORT VTKFILTERSPARALLEL_EXPORT __attribute__ ((__deprecated__))
#  define VTKFILTERSPARALLEL_DEPRECATED_NO_EXPORT VTKFILTERSPARALLEL_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKFILTERSPARALLEL_NO_DEPRECATED
#endif

/* AutoInit dependencies.  */
#include "vtkFiltersCoreModule.h"
#include "vtkFiltersExtractionModule.h"
#include "vtkFiltersGeneralModule.h"
#include "vtkFiltersModelingModule.h"

#endif
