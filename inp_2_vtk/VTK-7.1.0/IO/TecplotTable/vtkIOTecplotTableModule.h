
#ifndef VTKIOTECPLOTTABLE_EXPORT_H
#define VTKIOTECPLOTTABLE_EXPORT_H

#ifdef VTKIOTECPLOTTABLE_STATIC_DEFINE
#  define VTKIOTECPLOTTABLE_EXPORT
#  define VTKIOTECPLOTTABLE_NO_EXPORT
#else
#  ifndef VTKIOTECPLOTTABLE_EXPORT
#    ifdef vtkIOTecplotTable_EXPORTS
        /* We are building this library */
#      define VTKIOTECPLOTTABLE_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKIOTECPLOTTABLE_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKIOTECPLOTTABLE_NO_EXPORT
#    define VTKIOTECPLOTTABLE_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKIOTECPLOTTABLE_DEPRECATED
#  define VTKIOTECPLOTTABLE_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKIOTECPLOTTABLE_DEPRECATED_EXPORT VTKIOTECPLOTTABLE_EXPORT __attribute__ ((__deprecated__))
#  define VTKIOTECPLOTTABLE_DEPRECATED_NO_EXPORT VTKIOTECPLOTTABLE_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKIOTECPLOTTABLE_NO_DEPRECATED
#endif



#endif
