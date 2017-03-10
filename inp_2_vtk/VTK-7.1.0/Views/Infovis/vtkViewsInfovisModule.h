
#ifndef VTKVIEWSINFOVIS_EXPORT_H
#define VTKVIEWSINFOVIS_EXPORT_H

#ifdef VTKVIEWSINFOVIS_STATIC_DEFINE
#  define VTKVIEWSINFOVIS_EXPORT
#  define VTKVIEWSINFOVIS_NO_EXPORT
#else
#  ifndef VTKVIEWSINFOVIS_EXPORT
#    ifdef vtkViewsInfovis_EXPORTS
        /* We are building this library */
#      define VTKVIEWSINFOVIS_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKVIEWSINFOVIS_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKVIEWSINFOVIS_NO_EXPORT
#    define VTKVIEWSINFOVIS_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKVIEWSINFOVIS_DEPRECATED
#  define VTKVIEWSINFOVIS_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKVIEWSINFOVIS_DEPRECATED_EXPORT VTKVIEWSINFOVIS_EXPORT __attribute__ ((__deprecated__))
#  define VTKVIEWSINFOVIS_DEPRECATED_NO_EXPORT VTKVIEWSINFOVIS_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKVIEWSINFOVIS_NO_DEPRECATED
#endif

/* AutoInit dependencies.  */
#include "vtkInteractionStyleModule.h"
#include "vtkRenderingContext2DModule.h"
#include "vtkViewsCoreModule.h"

#endif
