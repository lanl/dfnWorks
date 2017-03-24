#ifndef _hotkey_h_
#define _hotkey_h_

extern struct termios orig_termios;
void reset_terminal_mode();
void set_conio_terminal_mode();
int kbhit();
int getch();

#endif
