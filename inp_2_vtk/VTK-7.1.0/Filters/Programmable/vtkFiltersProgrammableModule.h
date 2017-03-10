
#ifndef VTKFILTERSPROGRAMMABLE_EXPORT_H
#define VTKFILTERSPROGRAMMABLE_EXPORT_H

#ifdef VTKFILTERSPROGRAMMABLE_STATIC_DEFINE
#  define VTKFILTERSPROGRAMMABLE_EXPORT
#  define VTKFILTERSPROGRAMMABLE_NO_EXPORT
#else
#  ifndef VTKFILTERSPROGRAMMABLE_EXPORT
#    ifdef vtkFiltersProgrammable_EXPORTS
        /* We are building this library */
#      define VTKFILTERSPROGRAMMABLE_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKFILTERSPROGRAMMABLE_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKFILTERSPROGRAMMABLE_NO_EXPORT
#    define VTKFILTERSPROGRAMMABLE_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKFILTERSPROGRAMMABLE_DEPRECATED
#  define VTKFILTERSPROGRAMMABLE_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKFILTERSPROGRAMMABLE_DEPRECATED_EXPORT VTKFILTERSPROGRAMMABLE_EXPORT __attribute__ ((__deprecated__))
#  define VTKFILTERSPROGRAMMABLE_DEPRECATED_NO_EXPORT VTKFILTERSPROGRAMMABLE_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKFILTERSPROGRAMMABLE_NO_DEPRECATED
#endif



#endif
