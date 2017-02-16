#include <unistd.h>
#include <stdio.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
main()
{
  char*   path = tmpnam(NULL);
  int     exitStatus = 1;

  if (path != NULL)
    {
    int   fd = open(path, O_RDWR | O_CREAT | O_TRUNC, 0666);

    if (fd != -1)
      {
      if (write(fd, "0", 1) == 1)
        {
        off_t   pos = lseek(fd, 0, SEEK_CUR);

        if (pos != (off_t)-1)
          {
          if (ftruncate(fd, 512) != -1)
            {
            if (pos == lseek(fd, 0, SEEK_CUR))
              {
              if (lseek(fd, 0, SEEK_SET) == 0)
                {
                char  buf[512];

                if (read(fd, buf, 512) == 512)
                  exitStatus = 0;
                }
              }
            }
          }
        }
      close(fd);
      unlink(path);
      }
    }

  return exitStatus;
}