set(vtkRenderingGL2PSOpenGL2_HEADERS_LOADED 1)
set(vtkRenderingGL2PSOpenGL2_HEADERS "vtkOpenGLGL2PSHelperImpl;vtkRenderingGL2PSOpenGL2ObjectFactory")

foreach(header ${vtkRenderingGL2PSOpenGL2_HEADERS})
  set(vtkRenderingGL2PSOpenGL2_HEADER_${header}_EXISTS 1)
endforeach()


set(vtkRenderingGL2PSOpenGL2_HEADER_vtkOpenGLGL2PSHelperImpl_WRAP_EXCLUDE 1)


