
#ifndef VTKCOMMONMATH_EXPORT_H
#define VTKCOMMONMATH_EXPORT_H

#ifdef VTKCOMMONMATH_STATIC_DEFINE
#  define VTKCOMMONMATH_EXPORT
#  define VTKCOMMONMATH_NO_EXPORT
#else
#  ifndef VTKCOMMONMATH_EXPORT
#    ifdef vtkCommonMath_EXPORTS
        /* We are building this library */
#      define VTKCOMMONMATH_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKCOMMONMATH_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKCOMMONMATH_NO_EXPORT
#    define VTKCOMMONMATH_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKCOMMONMATH_DEPRECATED
#  define VTKCOMMONMATH_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKCOMMONMATH_DEPRECATED_EXPORT VTKCOMMONMATH_EXPORT __attribute__ ((__deprecated__))
#  define VTKCOMMONMATH_DEPRECATED_NO_EXPORT VTKCOMMONMATH_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKCOMMONMATH_NO_DEPRECATED
#endif



#endif
