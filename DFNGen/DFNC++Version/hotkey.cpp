#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/select.h>
#include <termios.h>
#include "hotkey.h"

//WARNING: NEEDS ERROR HANDLING

/***********************************************/
/*! Restores original terminal settings */
void reset_terminal_mode()
{
    // load original terminal settings
    tcsetattr(0, TCSANOW, &orig_termios);
}


/***********************************************/
/*! Sets custom terminal settings.
    This allows us to listen for a key press 
    without halting execution of program */
void set_conio_terminal_mode()
{
    struct termios new_termios;

    /* take two copies - one for now, one for later */
    tcgetattr(0, &orig_termios);
    memcpy(&new_termios, &orig_termios, sizeof(new_termios));

    /* register cleanup handler, and set the new terminal mode */
    new_termios.c_iflag &= ~(IGNBRK | BRKINT | PARMRK | ISTRIP | INLCR | IGNCR | ICRNL | IXON);
    new_termios.c_oflag |= ONLCR; 
    new_termios.c_lflag &= ~(ECHO | ECHONL | ICANON | ISIG | IEXTEN);
    new_termios.c_cflag &= ~(CSIZE | PARENB);
    new_termios.c_cflag |= CS8;
    tcsetattr(0, TCSANOW, &new_termios);
}


/***********************************************/
/*! Check if a key has been pressed. 
    Returns non-zero on key press.*/
int kbhit()
{
    struct timeval tv = { 0L, 0L };
    fd_set fds;
    FD_ZERO(&fds);
    FD_SET(0, &fds);
    return select(1, &fds, NULL, NULL, &tv);
}


/***********************************************/
/*! Get char of key press.
    Returns char as int. */
int getch()
{
    int r;
    unsigned char c;
    if ((r = read(0, &c, sizeof(c))) < 0) {
        return r;
    } else {
        return c;
    }
}


