
#ifndef VTKIMAGINGGENERAL_EXPORT_H
#define VTKIMAGINGGENERAL_EXPORT_H

#ifdef VTKIMAGINGGENERAL_STATIC_DEFINE
#  define VTKIMAGINGGENERAL_EXPORT
#  define VTKIMAGINGGENERAL_NO_EXPORT
#else
#  ifndef VTKIMAGINGGENERAL_EXPORT
#    ifdef vtkImagingGeneral_EXPORTS
        /* We are building this library */
#      define VTKIMAGINGGENERAL_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKIMAGINGGENERAL_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKIMAGINGGENERAL_NO_EXPORT
#    define VTKIMAGINGGENERAL_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKIMAGINGGENERAL_DEPRECATED
#  define VTKIMAGINGGENERAL_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKIMAGINGGENERAL_DEPRECATED_EXPORT VTKIMAGINGGENERAL_EXPORT __attribute__ ((__deprecated__))
#  define VTKIMAGINGGENERAL_DEPRECATED_NO_EXPORT VTKIMAGINGGENERAL_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKIMAGINGGENERAL_NO_DEPRECATED
#endif



#endif
