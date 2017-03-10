
#ifndef VTKIOXMLPARSER_EXPORT_H
#define VTKIOXMLPARSER_EXPORT_H

#ifdef VTKIOXMLPARSER_STATIC_DEFINE
#  define VTKIOXMLPARSER_EXPORT
#  define VTKIOXMLPARSER_NO_EXPORT
#else
#  ifndef VTKIOXMLPARSER_EXPORT
#    ifdef vtkIOXMLParser_EXPORTS
        /* We are building this library */
#      define VTKIOXMLPARSER_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKIOXMLPARSER_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKIOXMLPARSER_NO_EXPORT
#    define VTKIOXMLPARSER_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKIOXMLPARSER_DEPRECATED
#  define VTKIOXMLPARSER_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKIOXMLPARSER_DEPRECATED_EXPORT VTKIOXMLPARSER_EXPORT __attribute__ ((__deprecated__))
#  define VTKIOXMLPARSER_DEPRECATED_NO_EXPORT VTKIOXMLPARSER_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKIOXMLPARSER_NO_DEPRECATED
#endif



#endif
