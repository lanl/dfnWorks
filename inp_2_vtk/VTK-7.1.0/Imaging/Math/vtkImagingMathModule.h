
#ifndef VTKIMAGINGMATH_EXPORT_H
#define VTKIMAGINGMATH_EXPORT_H

#ifdef VTKIMAGINGMATH_STATIC_DEFINE
#  define VTKIMAGINGMATH_EXPORT
#  define VTKIMAGINGMATH_NO_EXPORT
#else
#  ifndef VTKIMAGINGMATH_EXPORT
#    ifdef vtkImagingMath_EXPORTS
        /* We are building this library */
#      define VTKIMAGINGMATH_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKIMAGINGMATH_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKIMAGINGMATH_NO_EXPORT
#    define VTKIMAGINGMATH_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKIMAGINGMATH_DEPRECATED
#  define VTKIMAGINGMATH_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKIMAGINGMATH_DEPRECATED_EXPORT VTKIMAGINGMATH_EXPORT __attribute__ ((__deprecated__))
#  define VTKIMAGINGMATH_DEPRECATED_NO_EXPORT VTKIMAGINGMATH_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKIMAGINGMATH_NO_DEPRECATED
#endif



#endif
