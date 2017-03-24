
#ifndef VTKDOMAINSCHEMISTRY_EXPORT_H
#define VTKDOMAINSCHEMISTRY_EXPORT_H

#ifdef VTKDOMAINSCHEMISTRY_STATIC_DEFINE
#  define VTKDOMAINSCHEMISTRY_EXPORT
#  define VTKDOMAINSCHEMISTRY_NO_EXPORT
#else
#  ifndef VTKDOMAINSCHEMISTRY_EXPORT
#    ifdef vtkDomainsChemistry_EXPORTS
        /* We are building this library */
#      define VTKDOMAINSCHEMISTRY_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKDOMAINSCHEMISTRY_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKDOMAINSCHEMISTRY_NO_EXPORT
#    define VTKDOMAINSCHEMISTRY_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKDOMAINSCHEMISTRY_DEPRECATED
#  define VTKDOMAINSCHEMISTRY_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKDOMAINSCHEMISTRY_DEPRECATED_EXPORT VTKDOMAINSCHEMISTRY_EXPORT __attribute__ ((__deprecated__))
#  define VTKDOMAINSCHEMISTRY_DEPRECATED_NO_EXPORT VTKDOMAINSCHEMISTRY_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKDOMAINSCHEMISTRY_NO_DEPRECATED
#endif

/* AutoInit dependencies.  */
#include "vtkRenderingCoreModule.h"

/* AutoInit implementations.  */
#if defined(vtkDomainsChemistry_INCLUDE)
# include vtkDomainsChemistry_INCLUDE
#endif
#if defined(vtkDomainsChemistry_AUTOINIT)
# include "vtkAutoInit.h"
VTK_AUTOINIT(vtkDomainsChemistry)
#endif

#endif
