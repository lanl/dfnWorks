
#ifndef VTKINFOVISCORE_EXPORT_H
#define VTKINFOVISCORE_EXPORT_H

#ifdef VTKINFOVISCORE_STATIC_DEFINE
#  define VTKINFOVISCORE_EXPORT
#  define VTKINFOVISCORE_NO_EXPORT
#else
#  ifndef VTKINFOVISCORE_EXPORT
#    ifdef vtkInfovisCore_EXPORTS
        /* We are building this library */
#      define VTKINFOVISCORE_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKINFOVISCORE_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKINFOVISCORE_NO_EXPORT
#    define VTKINFOVISCORE_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKINFOVISCORE_DEPRECATED
#  define VTKINFOVISCORE_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKINFOVISCORE_DEPRECATED_EXPORT VTKINFOVISCORE_EXPORT __attribute__ ((__deprecated__))
#  define VTKINFOVISCORE_DEPRECATED_NO_EXPORT VTKINFOVISCORE_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKINFOVISCORE_NO_DEPRECATED
#endif



#endif
