
#ifndef VTKIMAGINGMORPHOLOGICAL_EXPORT_H
#define VTKIMAGINGMORPHOLOGICAL_EXPORT_H

#ifdef VTKIMAGINGMORPHOLOGICAL_STATIC_DEFINE
#  define VTKIMAGINGMORPHOLOGICAL_EXPORT
#  define VTKIMAGINGMORPHOLOGICAL_NO_EXPORT
#else
#  ifndef VTKIMAGINGMORPHOLOGICAL_EXPORT
#    ifdef vtkImagingMorphological_EXPORTS
        /* We are building this library */
#      define VTKIMAGINGMORPHOLOGICAL_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKIMAGINGMORPHOLOGICAL_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKIMAGINGMORPHOLOGICAL_NO_EXPORT
#    define VTKIMAGINGMORPHOLOGICAL_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKIMAGINGMORPHOLOGICAL_DEPRECATED
#  define VTKIMAGINGMORPHOLOGICAL_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKIMAGINGMORPHOLOGICAL_DEPRECATED_EXPORT VTKIMAGINGMORPHOLOGICAL_EXPORT __attribute__ ((__deprecated__))
#  define VTKIMAGINGMORPHOLOGICAL_DEPRECATED_NO_EXPORT VTKIMAGINGMORPHOLOGICAL_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKIMAGINGMORPHOLOGICAL_NO_DEPRECATED
#endif



#endif
