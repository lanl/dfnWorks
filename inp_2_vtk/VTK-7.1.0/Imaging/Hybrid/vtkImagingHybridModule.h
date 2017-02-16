
#ifndef VTKIMAGINGHYBRID_EXPORT_H
#define VTKIMAGINGHYBRID_EXPORT_H

#ifdef VTKIMAGINGHYBRID_STATIC_DEFINE
#  define VTKIMAGINGHYBRID_EXPORT
#  define VTKIMAGINGHYBRID_NO_EXPORT
#else
#  ifndef VTKIMAGINGHYBRID_EXPORT
#    ifdef vtkImagingHybrid_EXPORTS
        /* We are building this library */
#      define VTKIMAGINGHYBRID_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKIMAGINGHYBRID_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKIMAGINGHYBRID_NO_EXPORT
#    define VTKIMAGINGHYBRID_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKIMAGINGHYBRID_DEPRECATED
#  define VTKIMAGINGHYBRID_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKIMAGINGHYBRID_DEPRECATED_EXPORT VTKIMAGINGHYBRID_EXPORT __attribute__ ((__deprecated__))
#  define VTKIMAGINGHYBRID_DEPRECATED_NO_EXPORT VTKIMAGINGHYBRID_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKIMAGINGHYBRID_NO_DEPRECATED
#endif



#endif
