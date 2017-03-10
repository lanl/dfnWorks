/* libsrc/ncconfig.in.  Generated automatically from configure.in by autoheader.  */
/* Id */
#ifndef _NCCONFIG_H_
#define _NCCONFIG_H_

#include "vtk_netcdf_config.h"
#include "vtk_netcdf_mangle.h"

/* Version number of package */
#define PACKAGE_VERSION "4.1.2"

#ifdef vtkNetCDF_EXPORTS
#  define DLL_EXPORT
#endif

/* Define if you're on an HP-UX system. */
/* #undef _HPUX_SOURCE */

/* Define if type char is unsigned and you are not using gcc.  */
#ifndef __CHAR_UNSIGNED__
/* #undef __CHAR_UNSIGNED__ */
#endif

/* Define if your struct stat has st_blksize.  */
#define HAVE_ST_BLKSIZE 1

/* Define to `long' if <sys/types.h> doesn't define.  */
/* #undef off_t */

/* Define to `unsigned' if <sys/types.h> doesn't define.  */
/* #undef size_t */

/* Define if you have the ANSI C header files.  */
#ifndef STDC_HEADERS
#define STDC_HEADERS 1
#endif

/* Define if your processor stores words with the most significant
   byte first (like Motorola and SPARC, unlike Intel and VAX).  */
/* All compilers that support Mac OS X define either __BIG_ENDIAN__ or
   __LITTLE_ENDIAN__ to match the endianness of the architecture being
   compiled for. This is not necessarily the same as the architecture of the
   machine doing the building. In order to support Universal Binaries on
   Mac OS X, we prefer those defines to decide the endianness.
   On other platforms we use the result of the TRY_RUN. */
#if !defined(__APPLE__)
/* #undef WORDS_BIGENDIAN */
#elif defined(__BIG_ENDIAN__)
#  define WORDS_BIGENDIAN 1
#endif

/* Define if you have <inttypes.h>  */
#define HAVE_INTTYPES_H 1

/* Define if you have <stdint.h>  */
#define HAVE_STDINT_H 1

/* Define if you don't have the <stdlib.h>.  */
/* #undef NO_STDLIB_H */

/* Define if you don't have the <sys/types.h>.  */
/* #undef NO_SYS_TYPES_H */

/* Define if you have the ftruncate function  */
#define HAVE_FTRUNCATE 1

/* Define if you have alloca, as a function or macro.  */
#define HAVE_ALLOCA 1

/* Define if you have <alloca.h> and it should be used (not on Ultrix).  */
#define HAVE_ALLOCA_H 1

/* Define if you have <unistd.h> and it should be used (not on Ultrix).  */
#define HAVE_UNISTD_H 1

/* Define if stdbool.h conforms to C99. */
#define HAVE_STDBOOL_H 1

/* Define if you don't have the strerror function  */
/* #undef NO_STRERROR */

/* Define if you have the strerror function  */
#define HAVE_STRERROR 1

/* Define if you want to use c++ API to netcdf3. */
#define CXX

/* Define if you want to use netcdf4. */
#define USE_NETCDF4

/* We do not support these pieces of netcdf yet. */
#undef cxx4
#undef UDUNITS
#undef LIBCF
#undef LIBCDMR
#undef USE_DAP
#undef USE_HDF4
#undef USE_PNETCDF

/* The hdf5 in vtk has 1.6 API so we have to set this to use it. */
#define H5_USE_16_API

/* Define if you have the <hdf5.h> header file. */
#define HAVE_HDF5_H

/* Define if you have the `hdf5' library (-lhdf5). */
#define HAVE_LIBHDF5

/* Define if you have the `hdf5_hl' library (-lhdf5_hl). */
#define HAVE_LIBHDF5_HL

/* Define to `int' if system doesn't define.  */
/* #undef ssize_t */

/* Define to `int' if system doesn't define.  */
/* #undef ptrdiff_t */

/* Define to 1 if the system has the type uchar. */
/* #undef HAVE_UCHAR */

/* Define to 1 if the system has the type `_Bool'. */
/* #undef HAVE__BOOL */

/* Define if the system does not use IEEE floating point representation */
/* #undef NO_IEEE_FLOAT */

/* Size of fundamental data types.  */
/* Mac OS X uses two data models, ILP32 (in which integers, long integers,
   and pointers are 32-bit quantities) and LP64 (in which integers are 32-bit
   quantities and long integers and pointers are 64-bit quantities). In order
   to support Universal Binaries on Mac OS X, we rely on this knowledge
   instead of testing the sizes of the building machine.
   On other platforms we use the result of the TRY_RUN. */
#if !defined(__APPLE__)
  #define SIZEOF_SHORT 2
  #define SIZEOF_INT 4
  #define SIZEOF_LONG 8
  #define SIZEOF_FLOAT 4
  #define SIZEOF_DOUBLE 8
  #define SIZEOF_SIZE_T 8
  #define SIZEOF_OFF_T 8
#else
#  define SIZEOF_SHORT   2
#  define SIZEOF_INT     4
#  if defined(__LP64__) && __LP64__
#    define SIZEOF_LONG   8
#    define SIZEOF_SIZE_T 8
#  else
#    define SIZEOF_LONG   4
#    define SIZEOF_SIZE_T 4
#  endif
#  define SIZEOF_FLOAT   4
#  define SIZEOF_DOUBLE  8
#  define SIZEOF_OFF_T   8
#endif

/* netcdf4's hdf5 cache parameters */
#define DEFAULT_CHUNK_SIZE 4194304
#define MAX_DEFAULT_CACHE_SIZE 67108864
#define DEFAULT_CHUNKS_IN_CACHE 10
#define CHUNK_CACHE_SIZE 4194304
#define CHUNK_CACHE_NELEMS 1009
#define CHUNK_CACHE_PREEMPTION 0.75

#endif /* !_NCCONFIG_H_ */
