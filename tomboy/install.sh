#!/bin/sh

mkdir -p ~/.config/tomboy/addins/

# Please install monodevelop to get mdtool.
# Please edit Zeitgeist.mdp and change the local path of Tomboy.exe
# to the correct one for your environment (so it can link to the 
# correct version of Tomboy).
mdtool build Zeitgeist.mdp

cp bin/Debug/Zeitgeist.dll ~/.config/tomboy/addins/Zeitgeist.dll 


