
#ifndef VTKIOXML_EXPORT_H
#define VTKIOXML_EXPORT_H

#ifdef VTKIOXML_STATIC_DEFINE
#  define VTKIOXML_EXPORT
#  define VTKIOXML_NO_EXPORT
#else
#  ifndef VTKIOXML_EXPORT
#    ifdef vtkIOXML_EXPORTS
        /* We are building this library */
#      define VTKIOXML_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKIOXML_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKIOXML_NO_EXPORT
#    define VTKIOXML_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKIOXML_DEPRECATED
#  define VTKIOXML_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKIOXML_DEPRECATED_EXPORT VTKIOXML_EXPORT __attribute__ ((__deprecated__))
#  define VTKIOXML_DEPRECATED_NO_EXPORT VTKIOXML_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKIOXML_NO_DEPRECATED
#endif



#endif
