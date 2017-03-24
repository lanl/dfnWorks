
#ifndef VTKIMAGINGCORE_EXPORT_H
#define VTKIMAGINGCORE_EXPORT_H

#ifdef VTKIMAGINGCORE_STATIC_DEFINE
#  define VTKIMAGINGCORE_EXPORT
#  define VTKIMAGINGCORE_NO_EXPORT
#else
#  ifndef VTKIMAGINGCORE_EXPORT
#    ifdef vtkImagingCore_EXPORTS
        /* We are building this library */
#      define VTKIMAGINGCORE_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKIMAGINGCORE_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKIMAGINGCORE_NO_EXPORT
#    define VTKIMAGINGCORE_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKIMAGINGCORE_DEPRECATED
#  define VTKIMAGINGCORE_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKIMAGINGCORE_DEPRECATED_EXPORT VTKIMAGINGCORE_EXPORT __attribute__ ((__deprecated__))
#  define VTKIMAGINGCORE_DEPRECATED_NO_EXPORT VTKIMAGINGCORE_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKIMAGINGCORE_NO_DEPRECATED
#endif



#endif
