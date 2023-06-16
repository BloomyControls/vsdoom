# Doom VeriStand Model

Sure, why not?

This model is generated and maintained using our VeriStand model generation
script: [BloomyControls/vsmodelgen][vsmodelgen]

[vsmodelgen]: https://github.com/BloomyControls/vsmodelgen

## Requirements

- VeriStand
- Linux RT model build support + tooling (available from NI)
- a cRIO or other Linux RT chassis compatible with VeriStand which has a video
  output
- a copy of Doom from which to source the DOOM.WAD file

The DOOM.WAD file must be placed on the target in the `/c` directory.

## Building

Modify `build_linux64.bat` with your VeriStand version (i.e., 2018). Then run
`build_linux64.bat`. You can then load and deploy the model, which will be
located at `build/linux64/libvsdoom64.so`.

## Modifying

To add inports, outports, signals, and parameters, simply add them to
`model.json` and run `python ./vsmodelgen.py -f -O src model.json`. You can then
modify `src/vsdoom.c` to your heart's content.

## Licensing

The model-specific code is licensed by Bloomy under the BSD 3-Clause license.
See LICENSE for details. All Doom source code is copyright Id Software. The
Doom source code license can be found in DOOMLIC.TXT (copied from the source
release). `genvsmodel.py` is licensed by Bloomy under the BSD 3-Clause license.
