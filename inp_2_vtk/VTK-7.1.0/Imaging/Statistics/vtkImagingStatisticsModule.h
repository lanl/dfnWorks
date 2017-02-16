
#ifndef VTKIMAGINGSTATISTICS_EXPORT_H
#define VTKIMAGINGSTATISTICS_EXPORT_H

#ifdef VTKIMAGINGSTATISTICS_STATIC_DEFINE
#  define VTKIMAGINGSTATISTICS_EXPORT
#  define VTKIMAGINGSTATISTICS_NO_EXPORT
#else
#  ifndef VTKIMAGINGSTATISTICS_EXPORT
#    ifdef vtkImagingStatistics_EXPORTS
        /* We are building this library */
#      define VTKIMAGINGSTATISTICS_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKIMAGINGSTATISTICS_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKIMAGINGSTATISTICS_NO_EXPORT
#    define VTKIMAGINGSTATISTICS_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKIMAGINGSTATISTICS_DEPRECATED
#  define VTKIMAGINGSTATISTICS_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKIMAGINGSTATISTICS_DEPRECATED_EXPORT VTKIMAGINGSTATISTICS_EXPORT __attribute__ ((__deprecated__))
#  define VTKIMAGINGSTATISTICS_DEPRECATED_NO_EXPORT VTKIMAGINGSTATISTICS_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKIMAGINGSTATISTICS_NO_DEPRECATED
#endif



#endif
