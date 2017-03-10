
#ifndef VTKINTERACTIONSTYLE_EXPORT_H
#define VTKINTERACTIONSTYLE_EXPORT_H

#ifdef VTKINTERACTIONSTYLE_STATIC_DEFINE
#  define VTKINTERACTIONSTYLE_EXPORT
#  define VTKINTERACTIONSTYLE_NO_EXPORT
#else
#  ifndef VTKINTERACTIONSTYLE_EXPORT
#    ifdef vtkInteractionStyle_EXPORTS
        /* We are building this library */
#      define VTKINTERACTIONSTYLE_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKINTERACTIONSTYLE_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKINTERACTIONSTYLE_NO_EXPORT
#    define VTKINTERACTIONSTYLE_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKINTERACTIONSTYLE_DEPRECATED
#  define VTKINTERACTIONSTYLE_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKINTERACTIONSTYLE_DEPRECATED_EXPORT VTKINTERACTIONSTYLE_EXPORT __attribute__ ((__deprecated__))
#  define VTKINTERACTIONSTYLE_DEPRECATED_NO_EXPORT VTKINTERACTIONSTYLE_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKINTERACTIONSTYLE_NO_DEPRECATED
#endif

/* AutoInit dependencies.  */
#include "vtkRenderingCoreModule.h"
#include "vtkRenderingCoreModule.h"

/* AutoInit implementations.  */
#if defined(vtkInteractionStyle_INCLUDE)
# include vtkInteractionStyle_INCLUDE
#endif
#if defined(vtkInteractionStyle_AUTOINIT)
# include "vtkAutoInit.h"
VTK_AUTOINIT(vtkInteractionStyle)
#endif

#endif
