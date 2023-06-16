@ECHO OFF

REM Auto-generated 64-bit Linux build file for vsdoom.
REM Generated Fri Jun 16 14:07:07 2023

SET BasePath="%~dp0"
REM drop the trailing \ on the path
SET BasePath="%BasePath:~0,-1%"

cd "%BasePath%"

REM change this to change your VeriStand version
SET VERISTAND_VERSION=2020

REM setup VeriStand environment and pass args to the makefile
cmd /k "C:\VeriStand\%VERISTAND_VERSION%\ModelInterface\tmw\toolchain\Linux_64_GNU_Setup.bat & cs-make.exe -f linux64.mak %*"
