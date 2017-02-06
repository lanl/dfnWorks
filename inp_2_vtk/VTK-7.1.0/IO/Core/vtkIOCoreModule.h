
#ifndef VTKIOCORE_EXPORT_H
#define VTKIOCORE_EXPORT_H

#ifdef VTKIOCORE_STATIC_DEFINE
#  define VTKIOCORE_EXPORT
#  define VTKIOCORE_NO_EXPORT
#else
#  ifndef VTKIOCORE_EXPORT
#    ifdef vtkIOCore_EXPORTS
        /* We are building this library */
#      define VTKIOCORE_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKIOCORE_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKIOCORE_NO_EXPORT
#    define VTKIOCORE_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKIOCORE_DEPRECATED
#  define VTKIOCORE_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKIOCORE_DEPRECATED_EXPORT VTKIOCORE_EXPORT __attribute__ ((__deprecated__))
#  define VTKIOCORE_DEPRECATED_NO_EXPORT VTKIOCORE_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKIOCORE_NO_DEPRECATED
#endif



#endif
