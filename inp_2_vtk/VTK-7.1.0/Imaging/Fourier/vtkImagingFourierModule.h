
#ifndef VTKIMAGINGFOURIER_EXPORT_H
#define VTKIMAGINGFOURIER_EXPORT_H

#ifdef VTKIMAGINGFOURIER_STATIC_DEFINE
#  define VTKIMAGINGFOURIER_EXPORT
#  define VTKIMAGINGFOURIER_NO_EXPORT
#else
#  ifndef VTKIMAGINGFOURIER_EXPORT
#    ifdef vtkImagingFourier_EXPORTS
        /* We are building this library */
#      define VTKIMAGINGFOURIER_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKIMAGINGFOURIER_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKIMAGINGFOURIER_NO_EXPORT
#    define VTKIMAGINGFOURIER_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKIMAGINGFOURIER_DEPRECATED
#  define VTKIMAGINGFOURIER_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKIMAGINGFOURIER_DEPRECATED_EXPORT VTKIMAGINGFOURIER_EXPORT __attribute__ ((__deprecated__))
#  define VTKIMAGINGFOURIER_DEPRECATED_NO_EXPORT VTKIMAGINGFOURIER_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKIMAGINGFOURIER_NO_DEPRECATED
#endif



#endif
