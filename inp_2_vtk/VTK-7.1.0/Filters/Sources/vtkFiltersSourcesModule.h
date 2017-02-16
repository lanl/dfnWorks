
#ifndef VTKFILTERSSOURCES_EXPORT_H
#define VTKFILTERSSOURCES_EXPORT_H

#ifdef VTKFILTERSSOURCES_STATIC_DEFINE
#  define VTKFILTERSSOURCES_EXPORT
#  define VTKFILTERSSOURCES_NO_EXPORT
#else
#  ifndef VTKFILTERSSOURCES_EXPORT
#    ifdef vtkFiltersSources_EXPORTS
        /* We are building this library */
#      define VTKFILTERSSOURCES_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKFILTERSSOURCES_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKFILTERSSOURCES_NO_EXPORT
#    define VTKFILTERSSOURCES_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKFILTERSSOURCES_DEPRECATED
#  define VTKFILTERSSOURCES_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKFILTERSSOURCES_DEPRECATED_EXPORT VTKFILTERSSOURCES_EXPORT __attribute__ ((__deprecated__))
#  define VTKFILTERSSOURCES_DEPRECATED_NO_EXPORT VTKFILTERSSOURCES_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKFILTERSSOURCES_NO_DEPRECATED
#endif



#endif
