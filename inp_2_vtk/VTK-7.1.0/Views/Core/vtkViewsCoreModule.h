
#ifndef VTKVIEWSCORE_EXPORT_H
#define VTKVIEWSCORE_EXPORT_H

#ifdef VTKVIEWSCORE_STATIC_DEFINE
#  define VTKVIEWSCORE_EXPORT
#  define VTKVIEWSCORE_NO_EXPORT
#else
#  ifndef VTKVIEWSCORE_EXPORT
#    ifdef vtkViewsCore_EXPORTS
        /* We are building this library */
#      define VTKVIEWSCORE_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKVIEWSCORE_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKVIEWSCORE_NO_EXPORT
#    define VTKVIEWSCORE_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKVIEWSCORE_DEPRECATED
#  define VTKVIEWSCORE_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKVIEWSCORE_DEPRECATED_EXPORT VTKVIEWSCORE_EXPORT __attribute__ ((__deprecated__))
#  define VTKVIEWSCORE_DEPRECATED_NO_EXPORT VTKVIEWSCORE_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKVIEWSCORE_NO_DEPRECATED
#endif

/* AutoInit dependencies.  */
#include "vtkInteractionWidgetsModule.h"

#endif
