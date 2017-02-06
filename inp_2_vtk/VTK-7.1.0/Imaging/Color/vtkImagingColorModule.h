
#ifndef VTKIMAGINGCOLOR_EXPORT_H
#define VTKIMAGINGCOLOR_EXPORT_H

#ifdef VTKIMAGINGCOLOR_STATIC_DEFINE
#  define VTKIMAGINGCOLOR_EXPORT
#  define VTKIMAGINGCOLOR_NO_EXPORT
#else
#  ifndef VTKIMAGINGCOLOR_EXPORT
#    ifdef vtkImagingColor_EXPORTS
        /* We are building this library */
#      define VTKIMAGINGCOLOR_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKIMAGINGCOLOR_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKIMAGINGCOLOR_NO_EXPORT
#    define VTKIMAGINGCOLOR_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKIMAGINGCOLOR_DEPRECATED
#  define VTKIMAGINGCOLOR_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKIMAGINGCOLOR_DEPRECATED_EXPORT VTKIMAGINGCOLOR_EXPORT __attribute__ ((__deprecated__))
#  define VTKIMAGINGCOLOR_DEPRECATED_NO_EXPORT VTKIMAGINGCOLOR_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKIMAGINGCOLOR_NO_DEPRECATED
#endif



#endif
