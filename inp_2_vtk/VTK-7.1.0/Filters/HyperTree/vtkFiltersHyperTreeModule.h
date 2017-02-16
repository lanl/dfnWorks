
#ifndef VTKFILTERSHYPERTREE_EXPORT_H
#define VTKFILTERSHYPERTREE_EXPORT_H

#ifdef VTKFILTERSHYPERTREE_STATIC_DEFINE
#  define VTKFILTERSHYPERTREE_EXPORT
#  define VTKFILTERSHYPERTREE_NO_EXPORT
#else
#  ifndef VTKFILTERSHYPERTREE_EXPORT
#    ifdef vtkFiltersHyperTree_EXPORTS
        /* We are building this library */
#      define VTKFILTERSHYPERTREE_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKFILTERSHYPERTREE_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKFILTERSHYPERTREE_NO_EXPORT
#    define VTKFILTERSHYPERTREE_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKFILTERSHYPERTREE_DEPRECATED
#  define VTKFILTERSHYPERTREE_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKFILTERSHYPERTREE_DEPRECATED_EXPORT VTKFILTERSHYPERTREE_EXPORT __attribute__ ((__deprecated__))
#  define VTKFILTERSHYPERTREE_DEPRECATED_NO_EXPORT VTKFILTERSHYPERTREE_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKFILTERSHYPERTREE_NO_DEPRECATED
#endif

/* AutoInit dependencies.  */
#include "vtkFiltersCoreModule.h"

#endif
