
#ifndef VTKFILTERSTEXTURE_EXPORT_H
#define VTKFILTERSTEXTURE_EXPORT_H

#ifdef VTKFILTERSTEXTURE_STATIC_DEFINE
#  define VTKFILTERSTEXTURE_EXPORT
#  define VTKFILTERSTEXTURE_NO_EXPORT
#else
#  ifndef VTKFILTERSTEXTURE_EXPORT
#    ifdef vtkFiltersTexture_EXPORTS
        /* We are building this library */
#      define VTKFILTERSTEXTURE_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKFILTERSTEXTURE_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKFILTERSTEXTURE_NO_EXPORT
#    define VTKFILTERSTEXTURE_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKFILTERSTEXTURE_DEPRECATED
#  define VTKFILTERSTEXTURE_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKFILTERSTEXTURE_DEPRECATED_EXPORT VTKFILTERSTEXTURE_EXPORT __attribute__ ((__deprecated__))
#  define VTKFILTERSTEXTURE_DEPRECATED_NO_EXPORT VTKFILTERSTEXTURE_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKFILTERSTEXTURE_NO_DEPRECATED
#endif



#endif
