/*
 * Auto-generated VeriStand model interface code for vsdoom.
 *
 * Generated Fri Jun 16 15:28:29 2023
 *
 * You almost certainly do NOT want to edit this file, as it may be overwritten
 * at any time!
 */

#include "ni_modelframework.h"
#include "model.h"

#include <stddef.h> /* offsetof() */

/* User-defined data types for parameters and signals */
#define rtDBL 0
#define rtINT 1

#ifdef __cplusplus
extern "C" {
#endif /* __cplusplus */

/* Model info */
const char* USER_ModelName DataSection(".NIVS.compiledmodelname") =
    "vsdoom";
const char* USER_Builder DataSection(".NIVS.builder") =
    "DOOM in VeriStand";


/* Model baserate */
double USER_BaseRate = 0.0025;

/* Model task configuration */
NI_Task rtTaskAttribs DataSection(".NIVS.tasklist") = {0, 0.0025, 0, 0};


/* Parameters */
int32_t ParameterSize DataSection(".NIVS.paramlistsize") = 0;
NI_Parameter rtParamAttribs[1] DataSection(".NIVS.paramlist");
int32_t ParamDimList[1] DataSection(".NIVS.paramdimlist");
Parameters initParams DataSection(".NIVS.defaultparams");
ParamSizeWidth Parameters_sizes[1] DataSection(".NIVS.defaultparamsizes");


/* Signals */
int32_t SignalSize DataSection(".NIVS.siglistsize") = 0;
NI_Signal rtSignalAttribs[1] DataSection(".NIVS.siglist");
int32_t SigDimList[1] DataSection(".NIVS.sigdimlist");


/* Inports and outports */
int32_t InportSize = 26;
int32_t OutportSize = 2;
int32_t ExtIOSize DataSection(".NIVS.extlistsize") = 28;
NI_ExternalIO rtIOAttribs[] DataSection(".NIVS.extlist") = {
  /* Inports */
  {0, "input/right", 0, 0, 1, 1, 1},
  {0, "input/left", 0, 0, 1, 1, 1},
  {0, "input/up", 0, 0, 1, 1, 1},
  {0, "input/down", 0, 0, 1, 1, 1},
  {0, "input/escape", 0, 0, 1, 1, 1},
  {0, "input/enter", 0, 0, 1, 1, 1},
  {0, "input/tab", 0, 0, 1, 1, 1},
  {0, "input/f1", 0, 0, 1, 1, 1},
  {0, "input/f2", 0, 0, 1, 1, 1},
  {0, "input/f3", 0, 0, 1, 1, 1},
  {0, "input/f4", 0, 0, 1, 1, 1},
  {0, "input/f5", 0, 0, 1, 1, 1},
  {0, "input/f6", 0, 0, 1, 1, 1},
  {0, "input/f7", 0, 0, 1, 1, 1},
  {0, "input/f8", 0, 0, 1, 1, 1},
  {0, "input/f9", 0, 0, 1, 1, 1},
  {0, "input/f10", 0, 0, 1, 1, 1},
  {0, "input/f11", 0, 0, 1, 1, 1},
  {0, "input/f12", 0, 0, 1, 1, 1},
  {0, "input/backspace", 0, 0, 1, 1, 1},
  {0, "input/pause", 0, 0, 1, 1, 1},
  {0, "input/equals", 0, 0, 1, 1, 1},
  {0, "input/minus", 0, 0, 1, 1, 1},
  {0, "input/rshift", 0, 0, 1, 1, 1},
  {0, "input/rctrl", 0, 0, 1, 1, 1},
  {0, "input/alt", 0, 0, 1, 1, 1},

  /* Outports */
  {0, "player/health", 0, 1, 1, 1, 1},
  {0, "player/armor", 0, 1, 1, 1, 1},

  /* Terminate list */
  {-1, NULL, 0, 0, 0, 0, 0},
};


int32_t USER_SetValueByDataType(void* ptr, int32_t idx, double value,
    int32_t type) {
  switch (type) {
    case rtDBL:
      ((double*)ptr)[idx] = (double)value;
      return NI_OK;
    case rtINT:
      ((int32_t*)ptr)[idx] = (int32_t)value;
      return NI_OK;
  }

  return NI_ERROR;
}

double USER_GetValueByDataType(void* ptr, int32_t idx, int32_t type) {
  switch (type) {
    case rtDBL:
      return ((double*)ptr)[idx];
    case rtINT:
      return (double)(((int32_t*)ptr)[idx]);
  }

  /* Return NaN on error */
  static const uint64_t nan = ~(uint64_t)0;
  return *(const double*)&nan;
}

int32_t USER_Initialize(void) {
  return vsdoom_Initialize();
}

int32_t USER_ModelStart(void) {
  return vsdoom_Start();
}

int32_t USER_TakeOneStep(double* inData, double* outData, double timestamp) {
  const struct Inports* inports = (const struct Inports*)inData;
  struct Outports* outports = (struct Outports*)outData;

  return vsdoom_Step(inports, outports, timestamp);
}

int32_t USER_Finalize(void) {
  return vsdoom_Finalize();
}

#ifdef __cplusplus
} /* extern "C" */
#endif /* __cplusplus */
