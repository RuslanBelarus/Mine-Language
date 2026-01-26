@echo off

echo Acess to folder update

rmdir /s project
mkdir project

echo folder making process...

cd project
mkdir building
mkdir release

echo Compiling process...

cd building
pyinstaller ../../main.py --onefile

echo Rest name process...

cd dist
ren "main.exe" "mlang.exe"

echo Files xcoping process...

cd ../../
xcopy building\dist\*.* release
copy ..\Studio.mh release

cd ..

echo Project was suffeculty compiled in folder: project\release