
#ifndef VTKINFOVISLAYOUT_EXPORT_H
#define VTKINFOVISLAYOUT_EXPORT_H

#ifdef VTKINFOVISLAYOUT_STATIC_DEFINE
#  define VTKINFOVISLAYOUT_EXPORT
#  define VTKINFOVISLAYOUT_NO_EXPORT
#else
#  ifndef VTKINFOVISLAYOUT_EXPORT
#    ifdef vtkInfovisLayout_EXPORTS
        /* We are building this library */
#      define VTKINFOVISLAYOUT_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKINFOVISLAYOUT_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKINFOVISLAYOUT_NO_EXPORT
#    define VTKINFOVISLAYOUT_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKINFOVISLAYOUT_DEPRECATED
#  define VTKINFOVISLAYOUT_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKINFOVISLAYOUT_DEPRECATED_EXPORT VTKINFOVISLAYOUT_EXPORT __attribute__ ((__deprecated__))
#  define VTKINFOVISLAYOUT_DEPRECATED_NO_EXPORT VTKINFOVISLAYOUT_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKINFOVISLAYOUT_NO_DEPRECATED
#endif



#endif
