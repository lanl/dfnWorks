
#ifndef VTKFILTERSEXTRACTION_EXPORT_H
#define VTKFILTERSEXTRACTION_EXPORT_H

#ifdef VTKFILTERSEXTRACTION_STATIC_DEFINE
#  define VTKFILTERSEXTRACTION_EXPORT
#  define VTKFILTERSEXTRACTION_NO_EXPORT
#else
#  ifndef VTKFILTERSEXTRACTION_EXPORT
#    ifdef vtkFiltersExtraction_EXPORTS
        /* We are building this library */
#      define VTKFILTERSEXTRACTION_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKFILTERSEXTRACTION_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKFILTERSEXTRACTION_NO_EXPORT
#    define VTKFILTERSEXTRACTION_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKFILTERSEXTRACTION_DEPRECATED
#  define VTKFILTERSEXTRACTION_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKFILTERSEXTRACTION_DEPRECATED_EXPORT VTKFILTERSEXTRACTION_EXPORT __attribute__ ((__deprecated__))
#  define VTKFILTERSEXTRACTION_DEPRECATED_NO_EXPORT VTKFILTERSEXTRACTION_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKFILTERSEXTRACTION_NO_DEPRECATED
#endif

/* AutoInit dependencies.  */
#include "vtkFiltersGeneralModule.h"

#endif
