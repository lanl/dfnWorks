
#ifndef VTKIOAMR_EXPORT_H
#define VTKIOAMR_EXPORT_H

#ifdef VTKIOAMR_STATIC_DEFINE
#  define VTKIOAMR_EXPORT
#  define VTKIOAMR_NO_EXPORT
#else
#  ifndef VTKIOAMR_EXPORT
#    ifdef vtkIOAMR_EXPORTS
        /* We are building this library */
#      define VTKIOAMR_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKIOAMR_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKIOAMR_NO_EXPORT
#    define VTKIOAMR_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKIOAMR_DEPRECATED
#  define VTKIOAMR_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKIOAMR_DEPRECATED_EXPORT VTKIOAMR_EXPORT __attribute__ ((__deprecated__))
#  define VTKIOAMR_DEPRECATED_NO_EXPORT VTKIOAMR_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKIOAMR_NO_DEPRECATED
#endif



#endif
