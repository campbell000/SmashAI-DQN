---
--- Created by ascam.
--- DateTime: 6/17/2018 12:30 PM
---

local current_loc = 0x01C044
local oneYpos_a = 0x01C070
local oneYpos_b = 0x01C074
local twoYpos_a = 0x01C078
local twoYpos_b = 0x01C07C
local ballYpos_a = 0x01C048
local ballYpos_b = 0x01C04C
local ballXpos_a = 0x01C050
local ballXpos_b = 0x01C054


-- For some reason, this game stores the player's y positions, and the ball's x/y coords in two different places,
-- and updates both of them in an alternating fashion (i.e. location a gets updated on frame one, location b gets updated
-- on frame 2, location a gets updated on frame 3, etc).
function get_player_1_ypos(resp)
    local loc = mainmemory.read_u32_be(current_loc)
    if (loc == 1) then
        return mainmemory.read_u32_be(oneYpos_a)
    end
    if (loc == 0) then
        return mainmemory.read_u32_be(oneYpos_b)
    end
end

function get_player_2_ypos(resp)
    local loc = mainmemory.read_u32_be(current_loc)
    if (loc == 1) then
        return mainmemory.read_u32_be(twoYpos_a)
    end
    if (loc == 0) then
        return mainmemory.read_u32_be(twoYpos_b)
    end
end

function get_ball_ypos(resp)
    local loc = mainmemory.read_u32_be(current_loc)
    if (loc == 1) then
        return mainmemory.read_u32_be(ballYpos_a)
    end
    if (loc == 0) then
        return mainmemory.read_u32_be(ballYpos_b)
    end
end

function get_ball_xpos(resp)
    local loc = mainmemory.read_u32_be(current_loc)
    if (loc == 1) then
        return mainmemory.read_u32_be(ballXpos_a)
    end
    if (loc == 0) then
        return mainmemory.read_u32_be(ballXpos_b)
    end
end


while true do
    gui.drawString(0,40, "Player 1: " .. get_player_1_ypos(player), null, null, 9)
    gui.drawString(0,50, "Player 2: " .. get_player_2_ypos(player), null, null, 9)
    gui.drawString(0,60, "Ball X: " .. get_ball_xpos(player), null, null, 9)
    gui.drawString(0,70, "Ball Y: " .. get_ball_ypos(player), null, null, 9)
    emu.frameadvance();
end