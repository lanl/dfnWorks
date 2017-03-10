
#ifndef VTKFILTERSAMR_EXPORT_H
#define VTKFILTERSAMR_EXPORT_H

#ifdef VTKFILTERSAMR_STATIC_DEFINE
#  define VTKFILTERSAMR_EXPORT
#  define VTKFILTERSAMR_NO_EXPORT
#else
#  ifndef VTKFILTERSAMR_EXPORT
#    ifdef vtkFiltersAMR_EXPORTS
        /* We are building this library */
#      define VTKFILTERSAMR_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKFILTERSAMR_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKFILTERSAMR_NO_EXPORT
#    define VTKFILTERSAMR_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKFILTERSAMR_DEPRECATED
#  define VTKFILTERSAMR_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKFILTERSAMR_DEPRECATED_EXPORT VTKFILTERSAMR_EXPORT __attribute__ ((__deprecated__))
#  define VTKFILTERSAMR_DEPRECATED_NO_EXPORT VTKFILTERSAMR_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKFILTERSAMR_NO_DEPRECATED
#endif



#endif
