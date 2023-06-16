#include <stdio.h>
#include <termios.h>

#include "doomdef.h"
#include "m_argv.h"
#include "d_main.h"

void I_StartTic (void)
{
    // event_t event = {0,0,0,0};
    // char key = getchar();
    // if (key != EOF)
    // {
    //          if (key == 'a') key = KEY_LEFTARROW;
    //     else if (key == 'd') key = KEY_RIGHTARROW;
    //     else if (key == 'w') key = KEY_UPARROW;
    //     else if (key == 's') key = KEY_DOWNARROW;

    //     event.type = ev_keydown;
    //     event.data1 = key;
    //     D_PostEvent(&event);

    //     event.type = ev_keyup;
    //     event.data1 = key;
    //     D_PostEvent(&event);
    // }
}
