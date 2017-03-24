
#ifndef VTKIOLSDYNA_EXPORT_H
#define VTKIOLSDYNA_EXPORT_H

#ifdef VTKIOLSDYNA_STATIC_DEFINE
#  define VTKIOLSDYNA_EXPORT
#  define VTKIOLSDYNA_NO_EXPORT
#else
#  ifndef VTKIOLSDYNA_EXPORT
#    ifdef vtkIOLSDyna_EXPORTS
        /* We are building this library */
#      define VTKIOLSDYNA_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKIOLSDYNA_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKIOLSDYNA_NO_EXPORT
#    define VTKIOLSDYNA_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKIOLSDYNA_DEPRECATED
#  define VTKIOLSDYNA_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKIOLSDYNA_DEPRECATED_EXPORT VTKIOLSDYNA_EXPORT __attribute__ ((__deprecated__))
#  define VTKIOLSDYNA_DEPRECATED_NO_EXPORT VTKIOLSDYNA_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKIOLSDYNA_NO_DEPRECATED
#endif



#endif
