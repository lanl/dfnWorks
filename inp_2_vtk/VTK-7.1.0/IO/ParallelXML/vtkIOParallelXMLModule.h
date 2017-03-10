
#ifndef VTKIOPARALLELXML_EXPORT_H
#define VTKIOPARALLELXML_EXPORT_H

#ifdef VTKIOPARALLELXML_STATIC_DEFINE
#  define VTKIOPARALLELXML_EXPORT
#  define VTKIOPARALLELXML_NO_EXPORT
#else
#  ifndef VTKIOPARALLELXML_EXPORT
#    ifdef vtkIOParallelXML_EXPORTS
        /* We are building this library */
#      define VTKIOPARALLELXML_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKIOPARALLELXML_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKIOPARALLELXML_NO_EXPORT
#    define VTKIOPARALLELXML_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKIOPARALLELXML_DEPRECATED
#  define VTKIOPARALLELXML_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKIOPARALLELXML_DEPRECATED_EXPORT VTKIOPARALLELXML_EXPORT __attribute__ ((__deprecated__))
#  define VTKIOPARALLELXML_DEPRECATED_NO_EXPORT VTKIOPARALLELXML_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKIOPARALLELXML_NO_DEPRECATED
#endif



#endif
