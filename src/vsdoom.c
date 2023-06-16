/*
 * Implementation of vsdoom.
 *
 * This file is safe to edit and will never be overwritten. Implement your model
 * logic here.
 *
 * Generated Fri Jun 16 14:05:30 2023
 */

#include "d_main.h"
#include "model.h"
#include "ni_modelframework.h"

extern void D_DoomLoop(void);

int32_t vsdoom_Initialize(void) {
  return NI_OK;
}

int32_t vsdoom_Start(void) {
  D_DoomMain();
  return NI_OK;
}

int32_t vsdoom_Step(const Inports* inports, double timestamp) {
  D_DoomLoop();
  return NI_OK;
}

int32_t vsdoom_Finalize(void) {
  return NI_OK;
}
