local lzw = require "lzw"

local a = "c[0][2xv]=0&c[0][2state]=10&c[0][1state]=10&c[0][1dir]=-1&c[0][2dmg]=0&c[0][2dir]=-1&c[0][2yp]=0&c[0][2is_air]=0&c[0][1char]=6&c[0][2char]=9&c[0][1yv]=0&c[0][1is_air]=0&c[0][2shld_rec]=0&c[0][1xv]=0&c[0][1ya]=0&c[0][1shld]=55&c[0][2shld]=55&c[0][2ya]=0&c[0][1dmg]=0&c[0][2yv]=0&c[0][1yp]=1542&c[0][1xp]=0&c[0][1state_frame]=5&c[0][2state_frame]=16&c[0][2xa]=0&c[0][2xp]=645.99658203125&c[0][1shld_rec]=0&c[0][1xa]=0&c[0][2jumps]=2&c[0][1jumps]=2&c[1][2xv]=0&c[1][2state]=10&c[1][1state]=10&c[1][1dir]=-1&c[1][2dmg]=0&c[1][2dir]=-1&c[1][2yp]=0&c[1][2is_air]=0&c[1][1char]=6&c[1][2char]=9&c[1][1yv]=0&c[1][1is_air]=0&c[1][2shld_rec]=0&c[1][1xv]=0&c[1][1ya]=0&c[1][1shld]=55&c[1][2shld]=55&c[1][2ya]=0&c[1][1dmg]=0&c[1][2yv]=0&c[1][1yp]=1542&c[1][1xp]=0&c[1][1state_frame]=6&c[1][2state_frame]=17&c[1][2xa]=0&c[1][2xp]=645.99658203125&c[1][1shld_rec]=0&c[1][1xa]=0&c[1][2jumps]=2&c[1][1jumps]=2&action=0&clientID=troblfshlgpn"
print(tostring(#a))
local b = lzw.deflate(a)
print(tostring(#b))
