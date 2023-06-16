#!/usr/bin/env python3

# VeriStand C/C++ Model Generation Utility
#
# https://github.com/BloomyControls/vsmodelgen
#
# Copyright (c) 2022, Bloomy Controls
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# You may copy this script into your own projects, provided you retain the above
# license.

from datetime import datetime
import argparse
import glob
import json
import os
import sys
import textwrap

parser = argparse.ArgumentParser(
        description="Generate VeriStand model boilerplate types/functions.",
        usage='%(prog)s [options] CONFIG')

parser.add_argument("config", metavar="CONFIG", type=argparse.FileType('r'),
        help="JSON model config file (or '-' to read from stdin)")

parser.add_argument('-r', "--root", type=str, default=os.getcwd(),
        metavar='DIR', dest='root_dir',
        help="project root directory (default: current working directory)")
parser.add_argument("-v", "--verbose", action='store_true',
        help="enable verbose output printed to stderr for debugging")

outputargs = parser.add_argument_group('output options',
        'Options controlling the output of the generated source.')
outputargs.add_argument("-f", "--force", action='store_true',
        help="overwrite output files if they exist")
outputargs.add_argument("-O", "--outdir", metavar="DIR", type=str,
        default="",
        help="directory to output source files to (default: project root)")
outputargs.add_argument("-o", metavar="FILE", type=str, dest='outsrcfile',
        default="model.c",
        help="name of the output model source file (default: %(default)s)")
outputargs.add_argument("-i", metavar="FILE", type=str, dest='outimplfile',
        default="",
        help="name of the output model implementation file (default: " +
        "<model_name>.c)")
outputargs.add_argument("-s", "--stdout", action='store_true',
        help="print generated output to stdout instead of files on disk")

genargs = parser.add_argument_group('generation options',
        'Options controlling the generated output.')
genargs.add_argument(f'--header', action=argparse.BooleanOptionalAction,
        dest="gen_header", default=True, help="generate model.h")
genargs.add_argument(f'--src', action=argparse.BooleanOptionalAction,
        dest="gen_src", default=True, help="generate model source file")
genargs.add_argument(f'--makefile', action=argparse.BooleanOptionalAction,
        dest="gen_makefile", default=False, help="generate makefile")
genargs.add_argument(f'--impl', action=argparse.BooleanOptionalAction,
        dest="gen_impl", default=False,
        help="generate boilerplate implementation of your model's required " +
        "functions (will NEVER override, even with --force specified)")

formatargs = parser.add_argument_group('formatting options',
        'Options controlling the formatting of the generated source.')
formatargs.add_argument("-t", "--tabs", action='store_true',
        help="use tabs to instead of spaces to indent generated code")
formatargs.add_argument("-w", "--indentwidth", metavar="N", type=int,
        default=2,
        help="number of spaces used to indent (default: %(default)s)")

makeargs = parser.add_argument_group('makefile options',
        textwrap.dedent("""
            Options controlling the generated makefile(s) (if enabled).

            Generated build files (Makefiles, build scripts, etc.) are stored in
            the project root specified by -r.

            By default (if -S and -I are not specified), the output directory
            specified by -O (or the current working directory if -O is not
            specified) is used for source files.

            Note: directories specified should be relative to the project root
            directory (specified by -r).
            """))
makeargs.add_argument('--cstd', type=str, default="c11",
        metavar='STD', help="C language standard (default: %(default)s)")
makeargs.add_argument('--cxxstd', type=str, default="c++14",
        metavar='STD', help="C++ language standard (default: %(default)s)")
makeargs.add_argument('-I', action='extend', type=str, default=[],
        metavar='DIR', dest='include_dirs',
        help="add a directory to search for includes in (may be specified " +
        "multiple tiles)")
makeargs.add_argument('-S', type=str, default="", metavar='DIR',
        dest='source_dir',
        help="add a directory to look for source files in")
makeargs.add_argument('-V', "--veristand-version", type=int, default=2018,
        metavar="YEAR", dest="veristand_version",
        help="VeriStand version to use (default: %(default)s)")
makeargs.add_argument('-B', "--bat", action='store_true', dest="gen_make_bat",
        help="generate build.bat script to use NI's toolchain to run the " +
        "generated makefiles")

args = parser.parse_args()

def Vprint(*objects, sep=' ', end='\n'):
    if args.verbose:
        print("info:", *objects, sep=sep, end=end, file=sys.stderr, flush=True)

def Eprint(*objects, sep=' ', end='\n'):
    print(*objects, sep=sep, end=end, file=sys.stderr, flush=True)

def Warn(msg: str):
    print("warning:", msg, file=sys.stderr, flush=True)

def Die(*objects, code=1):
    Eprint("error:", *objects)
    exit(code)

def Timestamp() -> str:
    now = datetime.now()
    return now.strftime("%a %b %d %H:%M:%S %Y")

# output source and header file paths
srcdir = os.path.join(args.root_dir, args.outdir)
outsrcfile = os.path.join(srcdir, args.outsrcfile)
outheaderfile = os.path.join(srcdir, "model.h")
outmakefile_linux64 = os.path.join(args.root_dir, "linux64.mak")
outmakefile_win = os.path.join(args.root_dir, "windows.mak")
outmakebat_linux64 = os.path.join(args.root_dir, "build_linux64.bat")
outmakebat_win32 = os.path.join(args.root_dir, "build_win_x86.bat")
outmakebat_win64 = os.path.join(args.root_dir, "build_win_x64.bat")

if not args.stdout:
    if args.gen_src: Vprint("output source file path:", outsrcfile)
    if args.gen_header: Vprint("output header file path:", outheaderfile)
    if args.gen_makefile:
        Vprint("output linux 64-bit makefile path:", outmakefile_linux64)
        Vprint("output windows makefile path:", outmakefile_win)
    if args.gen_make_bat:
        Vprint("output linux 64-bit batch file path:", outmakebat_linux64)
        Vprint("output win32 batch file path:", outmakebat_win32)
        Vprint("output win64 batch file path:", outmakebat_win64)

    if not args.force:
        if args.gen_src and os.path.exists(outsrcfile):
            Eprint(f"output file {outsrcfile} exists, not overwriting")
            Eprint("use -f to override this behavior")
            exit(1)

        if args.gen_header and os.path.exists(outheaderfile):
            Eprint(f"output file {outheaderfile} exists, not overwriting")
            Eprint("use -f to override this behavior")
            exit(1)

        if args.gen_makefile:
            for f in [outmakefile_linux64, outmakefile_win]:
                if os.path.exists(f):
                    Eprint(f"output file {f} exists, not overwriting")
                    Eprint("use -f to override this behavior")
                    exit(1)
        if args.gen_make_bat:
            for f in [outmakebat_linux64, outmakebat_win32, outmakebat_win64]:
                if os.path.exists(f):
                    Eprint(f"output file {f} exists, not overwriting")
                    Eprint("use -f to override this behavior")
                    exit(1)

    else:
        if args.gen_src and os.path.exists(outsrcfile):
            print(f"{outsrcfile} exists and will be overwritten (-f)")

        if args.gen_header and os.path.exists(outheaderfile):
            print(f"{outheaderfile} exists and will be overwritten (-f)")

        if args.gen_makefile:
            for f in [outmakefile_linux64, outmakefile_win]:
                if os.path.exists(f):
                    print(f"{f} exists and will be overwritten (-f)")

        if args.gen_make_bat:
            for f in [outmakebat_linux64, outmakebat_win32, outmakebat_win64]:
                if os.path.exists(f):
                    print(f"{f} exists and will be overwritten (-f)")
else:
    Vprint("output will be written to stdout")


# load config from JSON file
config = json.load(args.config)

if not "name" in config:
    Die("config does not define a model name")
else:
    if not str(config["name"]).isidentifier():
        Die("model name is not a valid identifier")

if not "builder" in config:
    Die("config does not define a model builder")
if not "baserate" in config:
    Die("config does not define a model baserate")

Vprint(f'model name: {config["name"]}')
Vprint(f'model builder: {config["builder"]}')
Vprint(f'model baserate: {config["baserate"]}')

outimplfile = os.path.join(srcdir, config["name"] + '.c')
if len(args.outimplfile) > 0:
    outimplfile = os.path.join(srcdir, args.outimplfile)

if args.gen_impl:
    Vprint("output boilerplate file path:", outimplfile)
    if os.path.exists(outimplfile):
        print(f"{outimplfile} exists and will NOT be overwritten!")
        args.gen_impl = False


def Expand(msg: str) -> str:
    """
    Expand tabs as specified by the user.

    :param msg: the string to indent
    :returns: the string with tabs expanded as necessary

    """
    msg = textwrap.dedent(msg).strip()
    if not args.tabs:
        return msg.expandtabs(max(0, args.indentwidth))
    else:
        return msg

def GetCategoryAndName(channel: str) -> tuple[str, str]:
    """
    Parse the name of an inport, outport, signal, or parameter into a category
    and a name.

    :param channel: the name of the inport, outport, signal, or parameter

    :returns: a tuple of ("category", "name")

    """
    if not "." in channel:
        if channel.isidentifier():
            return (":default", channel)
        else:
            Die(f"{channel} is not a valid identifier")
    else:
        parts = channel.split(".")
        if len(parts) == 2:
            (cat, name) = parts
            if not cat.isidentifier():
                Die(f"'{channel}': '{cat}' is not a valid identifier")
            elif not name.isidentifier():
                Die(f"'{channel}': '{name}' is not a valid identifier")
            else:
                return (cat, name)
        else:
            Die(f"'{channel}': names cannot contain more than one '.'")

def ParseChannels(channels, desc=False, types=False) -> dict:
    """
    Parse channels (inports, outports, signals, parameters) from the
    JSON config data.

    :param channels: array of objects from JSON
    :type channels: list
    :param desc: whether or not this channel type has a definition field (i.e.
    signals) (Default value = False)
    :param types: whether or not this channel type has a type field (i.e.
    signals and parameters) (Default value = False)

    :returns: a dictionary mapping categories to lists of objects containing
    name, dimX>=1, dimY>=1, and optionally a description and a type

    """
    outdata = {}

    for channel in channels:
        dimX = 1
        dimY = 1
        cat = None
        name = None
        description = None
        datatype = "double"

        if isinstance(channel, dict):
            if "name" in channel:
                (cat, name) = GetCategoryAndName(str(channel["name"]))
            else:
                Die("unnamed port, signal, or parameter")

            if desc and "description" in channel:
                description = str(channel["description"])
            elif not desc and "description" in channel:
                Warn(f"{channel['name']}: ignoring description field")

            if types and "type" in channel:
                if channel["type"] == "i32":
                    datatype = "int32_t"
                elif channel["type"] == "double":
                    datatype = "double"
                else:
                    Die(f"{channel['name']}: unknown type: {channel['type']}")
            elif not types and "type" in channel:
                Warn(f"{channel['name']}: ignoring type field")

            if "dimX" in channel:
                dimX = int(channel["dimX"])
            if "dimY" in channel:
                dimY = int(channel["dimY"])
            if dimX < 1:
                Die(f"{channel['name']}: dimX cannot be less than 1")
            if dimY < 1:
                Die(f"{channel['name']}: dimY cannot be less than 1")
        elif isinstance(channel, str):
            (cat, name) = GetCategoryAndName(channel)

        if not cat is None:
            chandata = {
                    "name": name,
                    "dimX": dimX,
                    "dimY": dimY,
                    }
            if desc:
                if description is None:
                    description = name
                chandata["description"] = description
            if types:
                chandata["type"] = datatype
            if not cat in outdata:
                outdata[cat] = []
            outdata[cat] += [chandata]

    return outdata

def ParsePorts(ports) -> dict:
    """
    Wraps around ParseChannels() to parse inports or outports.

    """
    return ParseChannels(ports, types=False, desc=False)

def ParseParameters(params) -> dict:
    """
    Wraps around ParseChannels() to parse parameters.

    """
    return ParseChannels(params, types=True, desc=False)

def ParseSignals(signals) -> dict:
    """
    Wraps around ParseChannels() to parse signals.

    """
    return ParseChannels(signals, desc=True, types=True)

def FmtChannelsStruct(valuedata, structname: str, types=False) -> str:
    """
    Format a dict of channels (inports, outports, signals, parameters)
    as returned by ParseChannels() into a C structure. This will be in the
    format `typedef struct structname {...} structname;`.

    Categories will be represented as sub-structures.

    If the struct name is "Parameters," the struct will contain one member even
    if there are no parameters. This is because the parameters type MUST exist,
    even if you have no parameters. Empty structs are allowed in C++, but not in
    C, so we add a dummy member for C compatibility.

    :param valuedata: dictionary containing definitions of categories and their
    values
    :type valuedata: dict
    :param structname: the name of the struct to create (must be a valid
    C identifier)
    :param types: whether or not to expect a type field in the definition for
    each value

    :returns: a string containing the struct definition

    """
    outstr = f'typedef struct {structname} {{\n'

    # add dummy member for empty parameters structs, since the struct must exist
    # even if we don't want it to
    if structname == "Parameters":
        if len(valuedata) == 0:
            outstr += '\t/* Empty structures are invalid in C */\n'
            outstr += '\tint dummy_param_;\n'

    for cat in valuedata:
        indentlevel = 1

        if cat == ":default":
            indentlevel = 1
        else:
            indentlevel = 2
            outstr += f'\tstruct {structname}_{cat} {{\n'

        for valdef in valuedata[cat]:
            datatype = "double"
            if types and "type" in valdef:
                datatype = valdef["type"]
            outstr += ("\t" * indentlevel) + f'{datatype} {valdef["name"]}'
            if valdef["dimX"] > 1 or valdef["dimY"] > 1:
                outstr += f'[{valdef["dimX"]}]'
            if valdef["dimY"] > 1:
                outstr += f'[{valdef["dimY"]}]'
            outstr += ';\n'

        if indentlevel == 2:
            outstr += f'\t}} {cat};\n'

    outstr += f"}} {structname};\n"
    return outstr

def FmtPortsStruct(ports, structname: str) -> str:
    """
    Format a struct for inports or outports using FmtChannelsStruct().

    :param structname: the name of the struct to create

    """
    return FmtChannelsStruct(ports, structname, types=False)

def FmtParametersStruct(params) -> str:
    """
    Format a struct for parameters using FmtChannelsStruct().

    """
    return FmtChannelsStruct(params, "Parameters", types=True)

def FmtSignalsStruct(signals) -> str:
    """
    Format a struct for signals using FmtChannelsStruct().

    """
    return FmtChannelsStruct(signals, "Signals", types=True)

def FmtExtIO(port, category: str, is_input: bool) -> str:
    """
    Format an entry in the generated ExtIO list. The result does not contain
    leading or trailing whitespace.

    :param port: the object containing the inport/outport data
    :type port: dict
    :param category: the category of the inport/outport
    :param is_input: whether or not this is an inport

    :returns: a string containing the generated ExtIO struct

    """
    catfield = category + '/' if category != ":default" else ""
    dirfield = 0 if is_input else 1
    dims = f'{port["dimX"]}, {port["dimY"]}'
    return f'{{0, "{catfield}{port["name"]}", 0, {dirfield}, 1, {dims}}}'

def FmtExtIOList(inports, outports) -> str:
    """
    Generates the ExtIO array from the given inports and outports. Also
    generates the variables defining the number of inports and outports.

    :param inports: list of inports
    :param outports: list of outports

    :returns: a string containing the generated ExtIO array

    """
    inportcount = 0
    outportcount = 0

    if len(inports) > 0:
        for cat in inports:
            inportcount += len(inports[cat])
    if len(outports) > 0:
        for cat in outports:
            outportcount += len(outports[cat])

    Vprint(f"found {inportcount} inports and {outportcount} outports")

    outstr = f'int32_t InportSize = {inportcount};\n'
    outstr += f'int32_t OutportSize = {outportcount};\n'
    outstr += 'int32_t ExtIOSize DataSection(".NIVS.extlistsize") = '
    outstr += f'{inportcount + outportcount};\n'
    outstr += f'NI_ExternalIO rtIOAttribs[] DataSection(".NIVS.extlist") = {{\n'

    if inportcount > 0:
        outstr += f'\t/* Inports */\n'
        for cat in inports:
            for port in inports[cat]:
                outstr += f'\t{FmtExtIO(port, cat, True)},\n'
        outstr += '\n'

    if outportcount > 0:
        outstr += f'\t/* Outports */\n'
        for cat in outports:
            for port in outports[cat]:
                outstr += f'\t{FmtExtIO(port, cat, False)},\n'
        outstr += '\n'

    outstr += f'\t/* Terminate list */\n'
    outstr += f'\t{{-1, NULL, 0, 0, 0, 0, 0}},\n}};\n'

    return outstr

def FmtParamAttribs(param, category: str, offset=0) -> str:
    """
    Generate a parameter attributes structure for a parameter definition.

    :param param: the parameter object
    :type param: dict
    :param category: the category this parameter is in
    :param offset: the offset field value (starts at 0, should increase by 2 for
    each entry in the list)

    :returns: a string containing the parameter attributes structure to be put
    into the array for VeriStand

    """
    catfield = category + '/' if category != ":default" else ""
    namefield = str(config["name"]) + '/' + catfield + param['name']
    structoffset = f'offsetof(Parameters, {param["name"]})'
    typefield = 'rtDBL' if param["type"] == "double" else 'rtINT'
    dim = param["dimX"] * param["dimY"]
    return '{{0, "{}", {}, {}, {}, 2, {}, 0}}'.format(
            namefield, structoffset, typefield, dim, offset)

def FmtParamList(params) -> str:
    """
    Generate the list of parameter attributes and the variables/definitions that
    go along with it.

    :param params: the list of parameter objects
    :type params: list

    :returns: a string containing the generated parameter configuration data

    """
    outstr = ''
    paramcount = 0

    for cat in params:
        paramcount += len(params[cat])

    Vprint(f"found {paramcount} parameters")

    outstr += 'int32_t ParameterSize DataSection(".NIVS.paramlistsize") = '
    outstr += f'{paramcount};\n'

    if paramcount == 0:
        outstr += 'NI_Parameter rtParamAttribs[1] '
        outstr += 'DataSection(".NIVS.paramlist");\n'
        outstr += 'int32_t ParamDimList[1] DataSection(".NIVS.paramdimlist");\n'
        outstr += 'Parameters initParams DataSection(".NIVS.defaultparams");\n'
        outstr += 'ParamSizeWidth Parameters_sizes[1] '
        outstr += 'DataSection(".NIVS.defaultparamsizes");\n'
    else:
        outstr += 'NI_Parameter rtParamAttribs[] DataSection(".NIVS.paramlist")'
        outstr += ' = {\n'
        offset = 0
        for cat in params:
            for param in params[cat]:
                outstr += f'\t{FmtParamAttribs(param, cat, offset)},\n'
                offset += 2
        outstr += '};\n'

        outstr += 'int32_t ParamDimList[] DataSection(".NIVS.paramdimlist")'
        outstr += ' = {\n'
        for cat in params:
            for param in params[cat]:
                outstr += f'\t{param["dimX"]:>2}, {param["dimY"]:>2}, '
                if cat != ':default':
                    outstr += f'/* {cat}.{param["name"]} */\n'
                else:
                    outstr += f'/* {param["name"]} */\n'
        outstr += '};\n'

        outstr += f'/* Set default parameter values here */\n'
        outstr += 'Parameters initParams DataSection(".NIVS.defaultparams");\n'

        outstr += 'ParamSizeWidth Parameters_sizes[] '
        outstr += 'DataSection(".NIVS.defaultparamsizes") = {\n'
        outstr += f'\t{{sizeof(Parameters), 0, 0}},\n'
        for cat in params:
            for param in params[cat]:
                ptype = 'rtDBL' if param["type"] == "double" else 'rtINT'
                dim = param["dimX"] * param["dimY"]
                outstr += f'\t{{sizeof({param["type"]}), {dim}, {ptype}}}, '
                if cat != ':default':
                    outstr += f'/* {cat}.{param["name"]} */\n'
                else:
                    outstr += f'/* {param["name"]} */\n'
        outstr += '};\n'

    return outstr

def FmtSignalAttribs(signal, category: str, offset=0) -> str:
    """
    Generate a signal attributes structure for a signal.

    :param signal: the signal object to use
    :type signal: dict
    :param category: the category this signal is in
    :param offset: the value of the offset field in the entry (should start at
    0 and increase by 2 for each entry)

    :returns a string containing the generated signal attributes structure

    """
    catfield = category + '/' if category != ":default" else ""
    namefield = str(config["name"]) + '/' + catfield + signal['name']
    typefield = 'rtDBL' if signal["type"] == "double" else 'rtINT'
    dim = signal["dimX"] * signal["dimY"]
    return '{{0, "{}", 0, "{}", 0, 0, {}, {}, 2, {}, 0}}'.format(
            namefield, signal["description"], typefield, dim, offset)

def FmtSignalList(signals) -> str:
    """
    Generate the signal list.

    :param signals: the list of signals
    :type signals: list

    :returns: a string containing the generated signal list and related
    configuration data

    """
    outstr = ''
    signalcount = 0

    for cat in signals:
        signalcount += len(signals[cat])

    Vprint(f"found {signalcount} signals")

    if signalcount > 0:
        outstr += 'Signals rtSignal;\n\n'

    outstr += 'int32_t SignalSize DataSection(".NIVS.siglistsize") = '
    outstr += f'{signalcount};\n'

    if signalcount == 0:
        outstr += 'NI_Signal rtSignalAttribs[1] DataSection(".NIVS.siglist");\n'
        outstr += 'int32_t SigDimList[1] DataSection(".NIVS.sigdimlist");\n'
    else:
        outstr += 'NI_Signal rtSignalAttribs[] DataSection(".NIVS.siglist")'
        outstr += ' = {\n'
        offset = 0
        for cat in signals:
            for sig in signals[cat]:
                outstr += f'\t{FmtSignalAttribs(sig, cat, offset)},\n'
                offset += 2
        outstr += '};\n'

        outstr += 'int32_t SigDimList[] DataSection(".NIVS.sigdimlist") = {\n'
        for cat in signals:
            for sig in signals[cat]:
                outstr += f'\t{sig["dimX"]:>2}, {sig["dimY"]:>2}, '
                if cat != ':default':
                    outstr += f'/* {cat}.{sig["name"]} */\n'
                else:
                    outstr += f'/* {sig["name"]} */\n'
        outstr += '};\n'

    return outstr

def FmtSignalInit(signals) -> str:
    """
    Generate the code used to configure pointers to signals in the
    initialization function.

    :param signals: list of signals
    :type signals: list

    :returns: the signal initialization code generated (beginning with
    a newline)

    """
    if len(signals) == 0:
        return ''

    outstr = '\n'
    outstr += '\t/* Populate pointers to signal values */\n'
    i = 0

    for cat in signals:
        for sig in signals[cat]:
            outstr += f'\trtSignalAttribs[{i}].addr = (uintptr_t)'
            prefix = ''
            if sig["dimX"] == 1 and sig["dimY"] == 1:
                prefix = '&'
            elif sig["dimX"] > 1 and sig["dimY"] == 1:
                prefix = ''
            elif sig["dimX"] > 1 and sig["dimY"] > 1:
                prefix = '*'
            catname = '' if cat == ':default' else '.' + cat
            outstr += f'{prefix}rtSignal{catname}.{sig["name"]};\n'
            i += 1

    return outstr


# data taken from the config
inports = {}
outports = {}
parameters = {}
signals = {}
baserate = float(config["baserate"])
if "inports" in config:
    inports = ParsePorts(config["inports"])
if "outports" in config:
    outports = ParsePorts(config["outports"])
if "parameters" in config:
    parameters = ParseParameters(config["parameters"])
if "signals" in config:
    signals = ParseSignals(config["signals"])

# generate an include guard based on the name of the model
incguard = f'{str(config["name"]).upper()}_MODEL_H'

if args.gen_header:
    Vprint(f"using {incguard} as model.h include guard")

# contents of the model.h file
output_model_h = f'''
/*
 * Auto-generated VeriStand model types for {config["name"]}.
 *
 * Generated {Timestamp()}
 *
 * You almost certainly do NOT want to edit this file, as it may be overwritten
 * at any time!
 */

#ifndef {incguard}
#define {incguard}

#include <stdint.h>

/* Parameters structure */
{FmtParametersStruct(parameters)}

/* Parameters are defined by NI model interface code */
/* Use readParam to access parameters */
extern Parameters rtParameter[2];
extern int32_t READSIDE;
#define readParam rtParameter[READSIDE]
'''

# add inports and outports only if applicable
inportsstruct = f'''
/* Inports structure */
{FmtPortsStruct(inports, "Inports")}
'''
if len(inports) > 0:
    output_model_h += inportsstruct

outportsstruct = f'''
/* Outports structure */
{FmtPortsStruct(outports, "Outports")}
'''
if len(outports) > 0:
    output_model_h += outportsstruct

signalsstruct = f'''
/* Signals structure */
{FmtSignalsStruct(signals)}
'''
# goes below in the extern "C" block if using C++ (fixes a bug with Windows x86)
signalsdecl = '''
/* Model signals */
extern Signals rtSignal;
'''
if len(signals) > 0:
    output_model_h += signalsstruct

output_model_h += f'''
#ifdef __cplusplus
extern "C" {{
#endif /* __cplusplus */
'''

if len(signals) > 0:
    output_model_h += signalsdecl

output_model_h += f'''
/* Your model code should define these functions. Return NI_OK or NI_ERROR. */
int32_t {config["name"]}_Initialize(void);
int32_t {config["name"]}_Start(void);'''

# model step function definition
stepfuncdef = f'int32_t {config["name"]}_Step('
if len(inports) > 0:
    stepfuncdef += 'const Inports* inports, '
if len(outports) > 0:
    stepfuncdef += 'Outports* outports, '
stepfuncdef += 'double timestamp)'

output_model_h += f'''
{stepfuncdef};
int32_t {config["name"]}_Finalize(void);

#ifdef __cplusplus
}} /* extern "C" */
#endif /* __cplusplus */

#endif /* {incguard} */
'''

# model source contents
output_model_src = f'''
/*
 * Auto-generated VeriStand model interface code for {config["name"]}.
 *
 * Generated {Timestamp()}
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
extern "C" {{
#endif /* __cplusplus */

/* Model info */
const char* USER_ModelName DataSection(".NIVS.compiledmodelname") =
\t\t"{config["name"]}";
const char* USER_Builder DataSection(".NIVS.builder") =
\t\t"{config["builder"]}";


/* Model baserate */
double USER_BaseRate = {baserate};

/* Model task configuration */
NI_Task rtTaskAttribs DataSection(".NIVS.tasklist") = {{0, {baserate}, 0, 0}};


/* Parameters */
{FmtParamList(parameters)}

/* Signals */
{FmtSignalList(signals)}

/* Inports and outports */
{FmtExtIOList(inports, outports)}

int32_t USER_SetValueByDataType(void* ptr, int32_t idx, double value,
\t\tint32_t type) {{
\tswitch (type) {{
\t\tcase rtDBL:
\t\t\t((double*)ptr)[idx] = (double)value;
\t\t\treturn NI_OK;
\t\tcase rtINT:
\t\t\t((int32_t*)ptr)[idx] = (int32_t)value;
\t\t\treturn NI_OK;
\t}}

\treturn NI_ERROR;
}}

double USER_GetValueByDataType(void* ptr, int32_t idx, int32_t type) {{
\tswitch (type) {{
\t\tcase rtDBL:
\t\t\treturn ((double*)ptr)[idx];
\t\tcase rtINT:
\t\t\treturn (double)(((int32_t*)ptr)[idx]);
\t}}

\t/* Return NaN on error */
\tstatic const uint64_t nan = ~(uint64_t)0;
\treturn *(const double*)&nan;
}}

int32_t USER_Initialize(void) {{{FmtSignalInit(signals)}
\treturn {config["name"]}_Initialize();
}}

int32_t USER_ModelStart(void) {{
\treturn {config["name"]}_Start();
}}

int32_t USER_TakeOneStep(double* inData, double* outData, double timestamp) {{
'''

inportscast = 'const struct Inports* inports = (const struct Inports*)inData;\n'
outportscast = 'struct Outports* outports = (struct Outports*)outData;\n'
if len(inports) > 0:
    output_model_src += '\t' + inportscast
else:
    output_model_src += '\t(void)inData; /* suppress unused variable */\n'

if len(outports) > 0:
    output_model_src += '\t' + outportscast
else:
    output_model_src += '\t(void)outData; /* suppress unused variable */\n'

output_model_src += f'''
\treturn {config["name"]}_Step('''
if len(inports) > 0:
    output_model_src += 'inports, '
if len(outports) > 0:
    output_model_src += 'outports, '
output_model_src += f'''timestamp);
}}

int32_t USER_Finalize(void) {{
\treturn {config["name"]}_Finalize();
}}

#ifdef __cplusplus
}} /* extern "C" */
#endif /* __cplusplus */
'''

output_model_impl = f'''
/*
 * Implementation of {config["name"]}.
 *
 * This file is safe to edit and will never be overwritten. Implement your model
 * logic here.
 *
 * Generated {Timestamp()}
 */

#include "ni_modelframework.h"
#include "model.h"

#ifdef __cplusplus
extern "C" {{
#endif /* __cplusplus */

int32_t {config["name"]}_Initialize(void) {{
\t/* TODO: Initialize your model here */
\treturn NI_OK;
}}

int32_t {config["name"]}_Start(void) {{
\t/* TODO: Prepare to start your model here */
\treturn NI_OK;
}}

{stepfuncdef} {{
\t/* TODO: Perform model steps here */
\treturn NI_OK;
}}

int32_t {config["name"]}_Finalize(void) {{
\t/* TODO: Cleanup your model here */
\treturn NI_OK;
}}

#ifdef __cplusplus
}} /* extern "C" */
#endif /* __cplusplus */
'''

if args.tabs:
    Vprint("indenting output with tabs")
else:
    Vprint(f"indenting output with {max(0, args.indentwidth)} spaces")

# generate the header and source files and print them to their intended
# destinations (either files or stdout) if they are enabled
if args.gen_header:
    output_model_h = Expand(output_model_h)
    linecount = len(output_model_h.splitlines())
    if args.stdout:
        print(output_model_h, file=sys.stdout)
    else:
        print(output_model_h, file=open(outheaderfile, 'w'))
        print(f"wrote {linecount} lines to {outheaderfile}")

if args.gen_src:
    output_model_src = Expand(output_model_src)
    linecount = len(output_model_src.splitlines())
    if args.stdout:
        print(output_model_src, file=sys.stdout)
    else:
        print(output_model_src, file=open(outsrcfile, 'w'))
        print(f"wrote {linecount} lines to {outsrcfile}")

if args.gen_impl:
    output_model_impl = Expand(output_model_impl)
    linecount = len(output_model_impl.splitlines())
    if args.stdout:
        print(output_model_impl, file=sys.stdout)
    else:
        print(output_model_impl, file=open(outimplfile, 'w'))
        print(f"wrote {linecount} lines to {outimplfile}")

def gen_makefile_linux64():
    if args.source_dir == "":
        if len(args.outdir) == 0:
            args.source_dir = "."
        else:
            args.source_dir = args.outdir

    sources = ""
    for ext in ['c', 'cpp', 'cc', 'cxx']:
        sources += f' $(wildcard {args.source_dir}/*.{ext})'

    includes = ""
    for inc in args.include_dirs:
        includes += f' "-I$(abspath {inc})"'

    makefile = f"""
    # Auto-generated 64-bit Linux Makefile for {config["name"]}.
    #
    # Generated {Timestamp()}

    # change this if you wish to update the veristand version used
    # (this is overridden by the value in build_linux64.bat)
    VERISTAND_VERSION ?= {args.veristand_version}

    CC = x86_64-nilrt-linux-gcc.exe
    CXX = x86_64-nilrt-linux-g++.exe

    # GCCSYSROOTPATH is generated from NI's bat files
    CXXFLAGS += -MMD -MP -W -Wall -pedantic -fPIC -std={args.cxxstd} \\
    \t--sysroot="$(subst \\,/,$(GCCSYSROOTPATH))" -fstrength-reduce \\
    \t-Os -fno-builtin -fno-strict-aliasing -fvisibility=protected

    CFLAGS += -MMD -MP -W -Wall -pedantic -fPIC -std={args.cstd} \\
    \t--sysroot="$(subst \\,/,$(GCCSYSROOTPATH))" -fstrength-reduce \\
    \t-Os -fno-builtin -fno-strict-aliasing -fvisibility=protected

    CPPFLAGS += -DkNIOSLinux

    RM := cs-rm -rf

    LDFLAGS += -fPIC -lrt -lpthread -lm -lc \\
    \t--sysroot="$(subst \\,/,$(GCCSYSROOTPATH))"

    # add include directories (-I/path/to/dir) here
    INCLUDES :={includes}

    # include directory for ni_modelframework.h
    NIVS_INC := "-IC:/VeriStand/$(VERISTAND_VERSION)/ModelInterface"

    # override this with environment variable if desired
    BUILDDIR ?= build/linux64

    SRC :={sources}
    OBJ := $(patsubst {args.source_dir}/%,$(BUILDDIR)/%.o,$(SRC))
    DEP := $(wildcard $(BUILDDIR)/*.d)

    NIVS_SRC := C:/VeriStand/$(VERISTAND_VERSION)/ModelInterface/custom/src/ni_modelframework.c
    NIVS_OBJ := $(BUILDDIR)/ni_modelframework.o

    TARGET := $(BUILDDIR)/lib{config["name"]}64.so

    .PHONY: all clean

    all: $(TARGET)

    $(TARGET): $(OBJ) $(NIVS_OBJ)
    \t@echo LINK\t$@
    \t@$(CXX) $(LDFLAGS) -shared -m64 -Wl,-soname,"$(@F)" -o "$@" $^

    -include $(DEP)

    $(NIVS_OBJ): $(NIVS_SRC) | $(BUILDDIR)
    \t@echo CC\t$@
    \t@$(CC) $(CFLAGS) $(CPPFLAGS) -D_XOPEN_SOURCE=700 -w "-I{args.source_dir}" $(NIVS_INC) -o "$@" -c "$<"

    define GEN_OBJ_TARGET
    $$(BUILDDIR)/%$(1).o: {args.source_dir}/%$(1) | $$(BUILDDIR)
    \t@echo $(2)\t$$@
    \t@$$($(2)) $$($(3)) $$(CPPFLAGS) $$(INCLUDES) $$(NIVS_INC) -o "$$@" -c "$$<"
    endef

    $(eval $(call GEN_OBJ_TARGET,.c,CC,CFLAGS))
    $(eval $(call GEN_OBJ_TARGET,.cpp,CXX,CXXFLAGS))
    $(eval $(call GEN_OBJ_TARGET,.cc,CXX,CXXFLAGS))
    $(eval $(call GEN_OBJ_TARGET,.cxx,CXX,CXXFLAGS))

    $(BUILDDIR):
    \t@echo MKDIR\t$@
    \t@mkdir "$@"

    clean:
    \t@echo RM\t$(BUILDDIR)
    \t@$(RM) -rf "$(BUILDDIR)"
    """

    makefile = textwrap.dedent(makefile).strip()
    linecount = len(makefile.splitlines())
    if args.stdout:
        print(makefile, file=sys.stdout)
    else:
        print(makefile, file=open(outmakefile_linux64, 'w'))
        print(f"wrote {linecount} lines to {outmakefile_linux64}")

def gen_makefile_win():
    if args.source_dir == "":
        if len(args.outdir) == 0:
            args.source_dir = "."
        else:
            args.source_dir = args.outdir

    args.source_dir = args.source_dir.replace('/', '\\')
    args.source_dir = args.source_dir.rstrip('\\ ')

    includes = ""
    for inc in args.include_dirs:
        _inc = inc.replace("/", "\\")
        includes += f' "/I{_inc}"'

    makefile = f"""
    # Auto-generated Windows x86 Makefile for {config["name"]}.
    #
    # Generated {Timestamp()}

    # this variable must always match the name of this file!
    THIS_FILE = windows.mak

    # change this if you wish to update the veristand version used
    # (this is overridden by the value in build_win_*.bat)
    !IFNDEF VERISTAND_VERSION
    VERISTAND_VERSION = {args.veristand_version}
    !ENDIF

    !IFNDEF WIN_ARCH
    !ERROR "WIN_ARCH not defined"
    !ENDIF

    CC = cl
    CXX = cl
    LD = link

    CFLAGS = /nologo /O2 /MD
    CXXFLAGS = /nologo /std:{args.cxxstd} /Zc:__cplusplus /O2 /MD /EHsc
    LDFLAGS = /nologo /dll /incremental:no

    # add include directories (/Ipath\\to\\dir) here
    INCLUDES ={includes}

    # include directory for ni_modelframework.h
    NIVS_INC = /IC:\\VeriStand\\$(VERISTAND_VERSION)\\ModelInterface

    # build directory
    BUILDDIR = build\\win_$(WIN_ARCH)

    NIVS_SRC = "C:\\VeriStand\\$(VERISTAND_VERSION)\\ModelInterface\\custom\\src\\ni_modelframework.c"
    NIVS_OBJ = $(BUILDDIR)\\ni_modelframework.obj

    TARGET = $(BUILDDIR)\\{config["name"]}_$(WIN_ARCH).dll

    all: $(BUILDDIR) _all_objs $(NIVS_OBJ) $(TARGET)

    # workaround to emulate wildcard searching for source files
    _all_objs: _cobjs _cppobjs _cxxobjs _ccobjs

    # wildcard each type of file and recursively make them
    obj_files=$(**:.c=.obj)
    _cobjs: {args.source_dir}\\*.c
    \t@IF NOT "$**"=="{args.source_dir}\\*.c" ( \\
    \t\t$(MAKE) /NOLOGO /F $(THIS_FILE) $(obj_files:{args.source_dir}\\=) \\
    \t)

    obj_files=$(**:.cpp=.obj)
    _cppobjs: {args.source_dir}\\*.cpp
    \t@IF NOT "$**"=="{args.source_dir}\\*.cpp" ( \\
    \t\t$(MAKE) /NOLOGO /F $(THIS_FILE) $(obj_files:{args.source_dir}\\=) \\
    \t)

    obj_files=$(**:.cxx=.obj)
    _cxxobjs: {args.source_dir}\\*.cxx
    \t@IF NOT "$**"=="{args.source_dir}\\*.cxx" ( \\
    \t\t$(MAKE) /NOLOGO /F $(THIS_FILE) $(obj_files:{args.source_dir}\\=) \\
    \t)

    obj_files=$(**:.cc=.obj)
    _ccobjs: {args.source_dir}\\*.cc
    \t@IF NOT "$**"=="{args.source_dir}\\*.cc" ( \\
    \t\t$(MAKE) /NOLOGO /F $(THIS_FILE) $(obj_files:{args.source_dir}\\=) \\
    \t)

    # dummy targets to keep nmake happy when files matching these patterns don't
    # exist
    {args.source_dir}\\*.c:

    {args.source_dir}\\*.cpp:

    {args.source_dir}\\*.cxx:

    {args.source_dir}\\*.cc:


    $(TARGET): $(BUILDDIR)\\*.obj
    \t@$(LD) $(LDFLAGS) /OUT:"$@" $**

    {{{args.source_dir}\\}}.cpp{{}}.obj:
    \t@$(CXX) $(CXXFLAGS) $(CPPFLAGS) $(INCLUDES) $(NIVS_INC) /Fo"$(BUILDDIR)\\$@" /c "$<"

    {{{args.source_dir}\\}}.cc{{}}.obj:
    \t@$(CXX) $(CXXFLAGS) $(CPPFLAGS) $(INCLUDES) $(NIVS_INC) /Fo"$(BUILDDIR)\\$@" /c "$<"

    {{{args.source_dir}\\}}.cxx{{}}.obj:
    \t@$(CXX) $(CXXFLAGS) $(CPPFLAGS) $(INCLUDES) $(NIVS_INC) /Fo"$(BUILDDIR)\\$@" /c "$<"

    {{{args.source_dir}\\}}.c{{}}.obj:
    \t@$(CC) $(CFLAGS) $(CPPFLAGS) $(INCLUDES) $(NIVS_INC) /Fo"$(BUILDDIR)\\$@" /c "$<"

    $(NIVS_OBJ): $(NIVS_SRC)
    \t@$(CC) $(CFLAGS) $(CPPFLAGS) /I{args.source_dir} $(NIVS_INC) /Fo"$@" /c $**

    $(BUILDDIR):
    \tMKDIR $@

    clean:
    \tDEL /Q $(BUILDDIR)
    """

    makefile = textwrap.dedent(makefile).strip()
    linecount = len(makefile.splitlines())
    if args.stdout:
        print(makefile, file=sys.stdout)
    else:
        print(makefile, file=open(outmakefile_win, 'w'))
        print(f"wrote {linecount} lines to {outmakefile_win}")

def gen_makebat_linux64():
    makebat = f"""
    @ECHO OFF

    REM Auto-generated 64-bit Linux build file for {config["name"]}.
    REM Generated {Timestamp()}

    SET BasePath="%~dp0"
    REM drop the trailing \\ on the path
    SET BasePath="%BasePath:~0,-1%"

    cd "%BasePath%"

    REM change this to change your VeriStand version
    SET VERISTAND_VERSION={args.veristand_version}

    REM setup VeriStand environment and pass args to the makefile
    cmd /k "C:\\VeriStand\\%VERISTAND_VERSION%\\ModelInterface\\tmw\\toolchain\\Linux_64_GNU_Setup.bat & cs-make.exe -f linux64.mak %*"
    """

    makebat = textwrap.dedent(makebat).strip()
    linecount = len(makebat.splitlines())
    if args.stdout:
        print(makebat, file=sys.stdout)
    else:
        print(makebat, file=open(outmakebat_linux64, 'w'))
        print(f"wrote {linecount} lines to {outmakebat_linux64}")

def gen_makebat_win(arch: str, outpath: str):
    makebat = f"""
    @ECHO OFF

    REM Auto-generated Windows {arch} build script for {config['name']}.
    REM Generated {Timestamp()}

    SETLOCAL ENABLEDELAYEDEXPANSION

    SET BasePath="%~dp0"
    REM drop the trailing \\ on the path
    SET BasePath="%BasePath:~0,-1%"

    cd "%BasePath%"

    REM change this to change your VeriStand version
    SET VERISTAND_VERSION={args.veristand_version}

    REM find VS tools 2017+
    REM https://docs.microsoft.com/en-us/cpp/build/building-on-the-command-line?view=msvc-170

    SET vers=(^
      2017^
      2019^
      2022^
    )

    SET editions=(^
      BuildTools^
      Professional^
      Enterprise^
      Community^
    )

    SET vsed=""
    SET vsver=0
    SET vcvars=""

    FOR %%v IN %vers% DO (
      FOR %%e IN %editions% DO (
        SET p="C:\\Program Files (x86)\\Microsoft Visual Studio\\%%v\\%%e\\VC\\Auxiliary\\Build\\vcvarsall.bat"
        IF EXIST !p! (
          SET vsed=%%e
          SET vsver=%%v
          SET vcvars=!p!
          GOTO Found
        )
      )
    )

    :NotFound
    ECHO No Visual Studio installation found! Make sure you have VS2017+ with
    ECHO the C/C++ development tools installed!

    exit /b 1

    :Found
    ECHO Found Visual Studio %vsed% %vsver% build tools

    SET WIN_ARCH={arch}
    cmd /K "%vcvars% {arch} & nmake /NOLOGO /F windows.mak %*"
    """

    makebat = textwrap.dedent(makebat).strip()
    linecount = len(makebat.splitlines())
    if args.stdout:
        print(makebat, file=sys.stdout)
    else:
        print(makebat, file=open(outpath, 'w'))
        print(f"wrote {linecount} lines to {outpath}")

if args.gen_makefile:
    gen_makefile_linux64()
    gen_makefile_win()

    if args.gen_make_bat:
        gen_makebat_linux64()
        gen_makebat_win('x86', outmakebat_win32)
        gen_makebat_win('x64', outmakebat_win64)
