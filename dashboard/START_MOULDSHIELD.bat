@echo off
setlocal
title MouldShield - 20261028-t20-t22
cd /d "%~dp0"
echo MouldShield 20261028-t20-t22 - opening the updated dashboard...
echo Use the address printed by this window. Close older MouldShield server windows.
call "%~dp0START_WINDOWS.bat" %*
