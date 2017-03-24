
#ifndef VTKCOMMONMISC_EXPORT_H
#define VTKCOMMONMISC_EXPORT_H

#ifdef VTKCOMMONMISC_STATIC_DEFINE
#  define VTKCOMMONMISC_EXPORT
#  define VTKCOMMONMISC_NO_EXPORT
#else
#  ifndef VTKCOMMONMISC_EXPORT
#    ifdef vtkCommonMisc_EXPORTS
        /* We are building this library */
#      define VTKCOMMONMISC_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKCOMMONMISC_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKCOMMONMISC_NO_EXPORT
#    define VTKCOMMONMISC_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKCOMMONMISC_DEPRECATED
#  define VTKCOMMONMISC_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKCOMMONMISC_DEPRECATED_EXPORT VTKCOMMONMISC_EXPORT __attribute__ ((__deprecated__))
#  define VTKCOMMONMISC_DEPRECATED_NO_EXPORT VTKCOMMONMISC_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKCOMMONMISC_NO_DEPRECATED
#endif



#endif
