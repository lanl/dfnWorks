
#ifndef VTKCOMMONSYSTEM_EXPORT_H
#define VTKCOMMONSYSTEM_EXPORT_H

#ifdef VTKCOMMONSYSTEM_STATIC_DEFINE
#  define VTKCOMMONSYSTEM_EXPORT
#  define VTKCOMMONSYSTEM_NO_EXPORT
#else
#  ifndef VTKCOMMONSYSTEM_EXPORT
#    ifdef vtkCommonSystem_EXPORTS
        /* We are building this library */
#      define VTKCOMMONSYSTEM_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKCOMMONSYSTEM_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKCOMMONSYSTEM_NO_EXPORT
#    define VTKCOMMONSYSTEM_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKCOMMONSYSTEM_DEPRECATED
#  define VTKCOMMONSYSTEM_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKCOMMONSYSTEM_DEPRECATED_EXPORT VTKCOMMONSYSTEM_EXPORT __attribute__ ((__deprecated__))
#  define VTKCOMMONSYSTEM_DEPRECATED_NO_EXPORT VTKCOMMONSYSTEM_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKCOMMONSYSTEM_NO_DEPRECATED
#endif



#endif
