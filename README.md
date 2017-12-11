# DeepLearningProject
This project includes a working copy of Bizhawk (the most recent at this point in time) and a working integration of luasockets. For whatever reason, this is difficult to do. So for convenience, I am uploading the entire bizhawk binary.

## IMPORTANT INFO FOR CS5984 INSTRUCTORS AND GRADERS:
This project contains many files: in addition to the learning/DQN code I wrote, I also uploaded the emulator and all of the libraries I used to this repo to make it easy for other people to set up this configuration (it was not easy). **For Grading Purposes, here are links to all of the contributions that I made for this project**:
- Youtube Link: https://www.youtube.com/watch?v=74TzP-3fQR8&feature=youtu.be
- Source Code of Interest:
    - Test
    - Test


## Essential Configuration
For now, we have to use the "faster, less reliable (memory leaks!)" version of Lua in Bizhawk. So, to configire Bizhawk and test that it's working, do the following:
- Load up the included PONG.V64 game (it's homebrew, so no need to arrest me).
- Go to "Tools > Customize > Advanced" and select the "Lua+LuaInterface" option.
- Restart the Emulator (you MUST do this)
- Load up the LuaConsole and load "test.lua". The console should return some HTTP-response stuff from google.com

# Seting up Bizhawk (if you don't want to use the Bizhawk build that I've uploaded here).
- Download Bizhawk 2.2.1. Other versions MIGHT work, but have not been tested
- Download the file at http://files.luaforge.net/releases/luasocket/luasocket/luasocket-2.0.2/luasocket-2.0.2-lua-5.1.2-Win32-vc8.zip
- Copy the contents of the "lua folder" into the "Lua" folder of your Bizhawk installation
- Put the "socket" and "mime" folders in the ROOT of your bizhawk installation directory. These should JUST contain DLLs.
- Follow the steps in "Essential Configuration" above.

# Credits
- Useful post for getting started: https://stackoverflow.com/questions/33428382/add-luasocket-to-program-bizhawk-shipped-with-own-lua-environment
- Good example of Lua+Bizhawk+Tensorflow in action: https://github.com/rameshvarun/NeuralKart. The author was also very helpful in answering some questions I had, and gave me the tip that his code only worked with Bizhawk 1.13.1. I eventually learned that later versions switched the Lua implementations, which led me to discover that switching the lua version eliminated the "dynamic libraries not supported" error.
