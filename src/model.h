/*
 * Auto-generated VeriStand model types for vsdoom.
 *
 * Generated Fri Jun 16 15:51:47 2023
 *
 * You almost certainly do NOT want to edit this file, as it may be overwritten
 * at any time!
 */

#ifndef VSDOOM_MODEL_H
#define VSDOOM_MODEL_H

#include <stdint.h>

/* Parameters structure */
typedef struct Parameters {
  /* Empty structures are invalid in C */
  int dummy_param_;
} Parameters;


/* Parameters are defined by NI model interface code */
/* Use readParam to access parameters */
extern Parameters rtParameter[2];
extern int32_t READSIDE;
#define readParam rtParameter[READSIDE]

/* Inports structure */
typedef struct Inports {
  struct Inports_input {
    double right;
    double left;
    double up;
    double down;
    double escape;
    double enter;
    double tab;
    double f1;
    double f2;
    double f3;
    double f4;
    double f5;
    double f6;
    double f7;
    double f8;
    double f9;
    double f10;
    double f11;
    double f12;
    double backspace;
    double pause;
    double equals;
    double minus;
    double rshift;
    double rctrl;
    double alt;
  } input;
  struct Inports_cheats {
    double noclip;
    double godmode;
  } cheats;
} Inports;


/* Outports structure */
typedef struct Outports {
  struct Outports_player {
    double health;
    double armor;
  } player;
} Outports;


/* Signals structure */
typedef struct Signals {
  struct Signals_debug {
    int32_t display_scale;
  } debug;
} Signals;


#ifdef __cplusplus
extern "C" {
#endif /* __cplusplus */

/* Model signals */
extern Signals rtSignal;

/* Your model code should define these functions. Return NI_OK or NI_ERROR. */
int32_t vsdoom_Initialize(void);
int32_t vsdoom_Start(void);
int32_t vsdoom_Step(const Inports* inports, Outports* outports, double timestamp);
int32_t vsdoom_Finalize(void);

#ifdef __cplusplus
} /* extern "C" */
#endif /* __cplusplus */

#endif /* VSDOOM_MODEL_H */
