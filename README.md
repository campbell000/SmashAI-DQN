# DQN Using Tensorflow and Emuhawk
This project contains code that trains DQN agents in a variety of N64 games, including Pong, Mario Tennis, and Super Smash Brothers. It consists of a python server (which does all the ML via tensorflow) and a lua client (runnable via EmuHawk's Lua Script Console). While this project may not ever be in "publishable" state, I think that the majority of it could be useful for those looking to use Deep Reinforcement Learning algorithms on NES, SNES, N64, and other classic console games.

## Notes on the Deep Q-Network implementation
Unlike the standard approach of using images, the majority of scripts included use values derived from memory locations (i.e. x position, health, time, etc). Since, theoretically, images are merely abstractions of those things, I would assume that this simply makes training go by much faster. There IS code here to send images back and forth, but it's much slower and not as well tested.

## The results
### Mario Tennis
Trained on a Hard Mario CPU (bot is Daisy)

Video: https://www.youtube.com/watch?v=4HNpX6kmq0Q

Averge Reward over time:

![Avg Reward](https://github.com/campbell000/DeepLearningProject/blob/master/python/scripts/results/mariotennis/iterations-vs-reward.png)

### Super Smash Brothers
Trained on a level 9 Pikachu (bot is Yoshi)

Video: https://www.youtube.com/watch?v=9P_Osy5-Fno

Averge Reward over time:

![Avg Reward](https://github.com/campbell000/DeepLearningProject/blob/master/python/scripts/iterations-vs-reward.png)

### Pong
Average Reward over Time:

![Avg Reward](https://github.com/campbell000/DeepLearningProject/blob/master/python/scripts/results/pong/dueling-huber-time-vs-reward.png)

## Essential Configuration
For now, we have to use the "faster, less reliable (memory leaks!)" version of Lua in Bizhawk. So, to configire Bizhawk and test that it's working, do the following:
- Load up the included PONG.V64 game (it's homebrew, so no need to arrest me).
- Go to "Tools > Customize > Advanced" and select the "Lua+LuaInterface" option.
- Restart the Emulator (you MUST do this)
- Load up the LuaConsole and load "test.lua". The console should return some HTTP-response stuff from google.com

## Seting up Bizhawk (if you don't want to use the Bizhawk build that I've uploaded here).
- Download Bizhawk 2.2.1. Other versions MIGHT work, but have not been tested
- Download the file at http://files.luaforge.net/releases/luasocket/luasocket/luasocket-2.0.2/luasocket-2.0.2-lua-5.1.2-Win32-vc8.zip
- Copy the contents of the "lua folder" into the "Lua" folder of your Bizhawk installation
- Put the "socket" and "mime" folders in the ROOT of your bizhawk installation directory. These should JUST contain DLLs.
- Follow the steps in "Essential Configuration" above.

## Troubleshooting
- If you get "%1 is not a valid Win32 Application" when downloading this repo and running the lua scripts in bizhawk, take the files from the luasockets64.zip folder and put them in the sockets/mime folders (overwriting the files already contained in them).

## Credits
- Useful post for getting me started: https://stackoverflow.com/questions/33428382/add-luasocket-to-program-bizhawk-shipped-with-own-lua-environment
- Good example of Lua+Bizhawk+Tensorflow in action: https://github.com/rameshvarun/NeuralKart. The author was also very helpful in answering some questions I had, and gave me the tip that his code only worked with Bizhawk 1.13.1. I eventually learned that later versions switched the Lua implementations, which led me to discover that switching the lua version eliminated the "dynamic libraries not supported" error.
- Very useful repo that provided me with memory addresses and functions for extracting the important game state values from memory: https://github.com/Isotarge/ScriptHawk
