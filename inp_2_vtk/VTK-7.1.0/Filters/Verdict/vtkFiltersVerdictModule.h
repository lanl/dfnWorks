
#ifndef VTKFILTERSVERDICT_EXPORT_H
#define VTKFILTERSVERDICT_EXPORT_H

#ifdef VTKFILTERSVERDICT_STATIC_DEFINE
#  define VTKFILTERSVERDICT_EXPORT
#  define VTKFILTERSVERDICT_NO_EXPORT
#else
#  ifndef VTKFILTERSVERDICT_EXPORT
#    ifdef vtkFiltersVerdict_EXPORTS
        /* We are building this library */
#      define VTKFILTERSVERDICT_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKFILTERSVERDICT_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKFILTERSVERDICT_NO_EXPORT
#    define VTKFILTERSVERDICT_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKFILTERSVERDICT_DEPRECATED
#  define VTKFILTERSVERDICT_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKFILTERSVERDICT_DEPRECATED_EXPORT VTKFILTERSVERDICT_EXPORT __attribute__ ((__deprecated__))
#  define VTKFILTERSVERDICT_DEPRECATED_NO_EXPORT VTKFILTERSVERDICT_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKFILTERSVERDICT_NO_DEPRECATED
#endif



#endif
