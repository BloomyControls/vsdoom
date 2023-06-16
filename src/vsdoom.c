/*
 * Implementation of vsdoom.
 *
 * This file is safe to edit and will never be overwritten. Implement your model
 * logic here.
 *
 * Generated Fri Jun 16 14:05:30 2023
 */

#include "d_main.h"
#include "doomdef.h"
#include "doomstat.h"
#include "i_video.h"
#include "model.h"
#include "ni_modelframework.h"

extern void D_DoomLoop(void);

static Inports curr_inports;
static Inports prev_inports;

// Returns 1 for a rising edge, -1 for a falling edge, and 0 for no change.
static int inport_edge(double prev, double curr) {
  if (prev == 0 && curr != 0) {
    return 1;
  } else if (prev != 0 && curr == 0) {
    return -1;
  } else {
    return 0;
  }
}

// Check for a change in an input and generate key up/down events if necessary.
static void check_input(double prev, double curr, int key) {
  int edge = inport_edge(prev, curr);
  if (edge > 0) {
    event_t event = {0, 0, 0, 0};
    event.type = ev_keydown;
    event.data1 = key;
    D_PostEvent(&event);
  } else if (edge < 0) {
    event_t event = {0, 0, 0, 0};
    event.type = ev_keyup;
    event.data1 = key;
    D_PostEvent(&event);
  }
}

void I_StartTic(void) {
#define CHECK_KEY(name,key) \
  check_input(prev_inports.input.name, curr_inports.input.name, key)
  CHECK_KEY(right, KEY_RIGHTARROW);
  CHECK_KEY(left, KEY_LEFTARROW);
  CHECK_KEY(up, KEY_UPARROW);
  CHECK_KEY(down, KEY_DOWNARROW);
  CHECK_KEY(escape, KEY_ESCAPE);
  CHECK_KEY(enter, KEY_ENTER);
  CHECK_KEY(tab, KEY_TAB);
  CHECK_KEY(f1, KEY_F1);
  CHECK_KEY(f2, KEY_F2);
  CHECK_KEY(f3, KEY_F3);
  CHECK_KEY(f4, KEY_F4);
  CHECK_KEY(f5, KEY_F5);
  CHECK_KEY(f6, KEY_F6);
  CHECK_KEY(f7, KEY_F7);
  CHECK_KEY(f8, KEY_F8);
  CHECK_KEY(f9, KEY_F9);
  CHECK_KEY(f10, KEY_F10);
  CHECK_KEY(f11, KEY_F11);
  CHECK_KEY(f12, KEY_F12);
  CHECK_KEY(backspace, KEY_BACKSPACE);
  CHECK_KEY(pause, KEY_PAUSE);
  CHECK_KEY(equals, KEY_EQUALS);
  CHECK_KEY(minus, KEY_MINUS);
  CHECK_KEY(rshift, KEY_RSHIFT);
  CHECK_KEY(rctrl, KEY_RCTRL);
  CHECK_KEY(alt, KEY_RALT);
#undef CHECK_KEY
}

int32_t vsdoom_Initialize(void) {
  return NI_OK;
}

int32_t vsdoom_Start(void) {
  D_DoomMain();
  rtSignal.debug.display_scale = screen_scale;
  return NI_OK;
}

int32_t vsdoom_Step(const Inports* inports, Outports* outports,
                    double timestamp) {
  curr_inports = *inports;
  player_t* plyr = &players[consoleplayer];
  D_DoomLoop();
  prev_inports = curr_inports;
  outports->player.health = plyr->health;
  outports->player.armor = plyr->armorpoints;
  return NI_OK;
}

int32_t vsdoom_Finalize(void) {
  return NI_OK;
}
