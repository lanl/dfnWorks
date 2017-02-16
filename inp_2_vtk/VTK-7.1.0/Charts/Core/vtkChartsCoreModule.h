
#ifndef VTKCHARTSCORE_EXPORT_H
#define VTKCHARTSCORE_EXPORT_H

#ifdef VTKCHARTSCORE_STATIC_DEFINE
#  define VTKCHARTSCORE_EXPORT
#  define VTKCHARTSCORE_NO_EXPORT
#else
#  ifndef VTKCHARTSCORE_EXPORT
#    ifdef vtkChartsCore_EXPORTS
        /* We are building this library */
#      define VTKCHARTSCORE_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKCHARTSCORE_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKCHARTSCORE_NO_EXPORT
#    define VTKCHARTSCORE_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKCHARTSCORE_DEPRECATED
#  define VTKCHARTSCORE_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKCHARTSCORE_DEPRECATED_EXPORT VTKCHARTSCORE_EXPORT __attribute__ ((__deprecated__))
#  define VTKCHARTSCORE_DEPRECATED_NO_EXPORT VTKCHARTSCORE_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKCHARTSCORE_NO_DEPRECATED
#endif

/* AutoInit dependencies.  */
#include "vtkFiltersGeneralModule.h"
#include "vtkRenderingContext2DModule.h"
#include "vtkRenderingCoreModule.h"

#endif
