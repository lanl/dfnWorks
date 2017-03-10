
#ifndef VTKIOEXPORT_EXPORT_H
#define VTKIOEXPORT_EXPORT_H

#ifdef VTKIOEXPORT_STATIC_DEFINE
#  define VTKIOEXPORT_EXPORT
#  define VTKIOEXPORT_NO_EXPORT
#else
#  ifndef VTKIOEXPORT_EXPORT
#    ifdef vtkIOExport_EXPORTS
        /* We are building this library */
#      define VTKIOEXPORT_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKIOEXPORT_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKIOEXPORT_NO_EXPORT
#    define VTKIOEXPORT_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKIOEXPORT_DEPRECATED
#  define VTKIOEXPORT_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKIOEXPORT_DEPRECATED_EXPORT VTKIOEXPORT_EXPORT __attribute__ ((__deprecated__))
#  define VTKIOEXPORT_DEPRECATED_NO_EXPORT VTKIOEXPORT_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKIOEXPORT_NO_DEPRECATED
#endif

/* AutoInit dependencies.  */
#include "vtkRenderingCoreModule.h"
#include "vtkRenderingGL2PSOpenGL2Module.h"

/* AutoInit implementations.  */
#if defined(vtkIOExport_INCLUDE)
# include vtkIOExport_INCLUDE
#endif
#if defined(vtkIOExport_AUTOINIT)
# include "vtkAutoInit.h"
VTK_AUTOINIT(vtkIOExport)
#endif

#endif
