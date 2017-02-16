
#ifndef VTKCOMMONDATAMODEL_EXPORT_H
#define VTKCOMMONDATAMODEL_EXPORT_H

#ifdef VTKCOMMONDATAMODEL_STATIC_DEFINE
#  define VTKCOMMONDATAMODEL_EXPORT
#  define VTKCOMMONDATAMODEL_NO_EXPORT
#else
#  ifndef VTKCOMMONDATAMODEL_EXPORT
#    ifdef vtkCommonDataModel_EXPORTS
        /* We are building this library */
#      define VTKCOMMONDATAMODEL_EXPORT __attribute__((visibility("default")))
#    else
        /* We are using this library */
#      define VTKCOMMONDATAMODEL_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef VTKCOMMONDATAMODEL_NO_EXPORT
#    define VTKCOMMONDATAMODEL_NO_EXPORT __attribute__((visibility("hidden")))
#  endif
#endif

#ifndef VTKCOMMONDATAMODEL_DEPRECATED
#  define VTKCOMMONDATAMODEL_DEPRECATED __attribute__ ((__deprecated__))
#  define VTKCOMMONDATAMODEL_DEPRECATED_EXPORT VTKCOMMONDATAMODEL_EXPORT __attribute__ ((__deprecated__))
#  define VTKCOMMONDATAMODEL_DEPRECATED_NO_EXPORT VTKCOMMONDATAMODEL_NO_EXPORT __attribute__ ((__deprecated__))
#endif

#define DEFINE_NO_DEPRECATED 0
#if DEFINE_NO_DEPRECATED
# define VTKCOMMONDATAMODEL_NO_DEPRECATED
#endif



#endif
