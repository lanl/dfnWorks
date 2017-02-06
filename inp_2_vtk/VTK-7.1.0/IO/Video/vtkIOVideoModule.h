
#ifndef VTKIOVIDEO_EXPORT_H
#define VTKIOVIDEO_EXPORT_H

#ifdef VTKIOVIDEO_STATIC_DEFINE
#  define VTKIOVIDEO_EXPORT
#  define VTKIOVIDEO_NO_EXPORT
#else
#  ifndef VTKIOVIDEO_EXPORT
#    ifdef vtkIOVideo_EXPORTS
        /* We are building this library */
#      define VTKIOVIDEO_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKIOVIDEO_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKIOVIDEO_NO_EXPORT
#    define VTKIOVIDEO_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKIOVIDEO_DEPRECATED
#  define VTKIOVIDEO_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKIOVIDEO_DEPRECATED_EXPORT VTKIOVIDEO_EXPORT __attribute__ ((__deprecated__))
#  define VTKIOVIDEO_DEPRECATED_NO_EXPORT VTKIOVIDEO_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKIOVIDEO_NO_DEPRECATED
#endif



#endif
