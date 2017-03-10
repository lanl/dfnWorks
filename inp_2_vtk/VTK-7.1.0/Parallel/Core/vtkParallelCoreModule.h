
#ifndef VTKPARALLELCORE_EXPORT_H
#define VTKPARALLELCORE_EXPORT_H

#ifdef VTKPARALLELCORE_STATIC_DEFINE
#  define VTKPARALLELCORE_EXPORT
#  define VTKPARALLELCORE_NO_EXPORT
#else
#  ifndef VTKPARALLELCORE_EXPORT
#    ifdef vtkParallelCore_EXPORTS
        /* We are building this library */
#      define VTKPARALLELCORE_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKPARALLELCORE_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKPARALLELCORE_NO_EXPORT
#    define VTKPARALLELCORE_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKPARALLELCORE_DEPRECATED
#  define VTKPARALLELCORE_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKPARALLELCORE_DEPRECATED_EXPORT VTKPARALLELCORE_EXPORT __attribute__ ((__deprecated__))
#  define VTKPARALLELCORE_DEPRECATED_NO_EXPORT VTKPARALLELCORE_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKPARALLELCORE_NO_DEPRECATED
#endif



#endif
