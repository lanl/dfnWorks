
#ifndef VTKFILTERSHYBRID_EXPORT_H
#define VTKFILTERSHYBRID_EXPORT_H

#ifdef VTKFILTERSHYBRID_STATIC_DEFINE
#  define VTKFILTERSHYBRID_EXPORT
#  define VTKFILTERSHYBRID_NO_EXPORT
#else
#  ifndef VTKFILTERSHYBRID_EXPORT
#    ifdef vtkFiltersHybrid_EXPORTS
        /* We are building this library */
#      define VTKFILTERSHYBRID_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKFILTERSHYBRID_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKFILTERSHYBRID_NO_EXPORT
#    define VTKFILTERSHYBRID_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKFILTERSHYBRID_DEPRECATED
#  define VTKFILTERSHYBRID_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKFILTERSHYBRID_DEPRECATED_EXPORT VTKFILTERSHYBRID_EXPORT __attribute__ ((__deprecated__))
#  define VTKFILTERSHYBRID_DEPRECATED_NO_EXPORT VTKFILTERSHYBRID_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKFILTERSHYBRID_NO_DEPRECATED
#endif



#endif
