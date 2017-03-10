
#ifndef VTKIOINFOVIS_EXPORT_H
#define VTKIOINFOVIS_EXPORT_H

#ifdef VTKIOINFOVIS_STATIC_DEFINE
#  define VTKIOINFOVIS_EXPORT
#  define VTKIOINFOVIS_NO_EXPORT
#else
#  ifndef VTKIOINFOVIS_EXPORT
#    ifdef vtkIOInfovis_EXPORTS
        /* We are building this library */
#      define VTKIOINFOVIS_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKIOINFOVIS_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKIOINFOVIS_NO_EXPORT
#    define VTKIOINFOVIS_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKIOINFOVIS_DEPRECATED
#  define VTKIOINFOVIS_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKIOINFOVIS_DEPRECATED_EXPORT VTKIOINFOVIS_EXPORT __attribute__ ((__deprecated__))
#  define VTKIOINFOVIS_DEPRECATED_NO_EXPORT VTKIOINFOVIS_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKIOINFOVIS_NO_DEPRECATED
#endif



#endif
