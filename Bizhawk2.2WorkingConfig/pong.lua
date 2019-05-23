-- This file reads game states variables from memory, and sends the game state to the Learning Server.

-- This only works for the USA rom
require "global";
require "gameConstants";
require "utils";
require "list"
local TF_CLIENT = require("tensorflow-client")
local tfServerSampleIteration = 0
local currentStateBuffer = List.newList()
local currentAction = 2 -- Start off doing nothing (PONG_INPUT_ORDER[2])
Game = {}

function RandomVariable(length)
    local res = ""
    for i = 1, length do
        res = res .. string.char(math.random(97, 122))
    end
    return res
end

-- CONSTANTS
-- This variable is the number of frames we skip before sending / receiving data from the tf server. Note that when this
-- number is > 1, this means that the bot will HOLD down the current action N number of frames
local TF_SERVER_SAMPLE_SKIP_RATE = 2

-- This variable is the number of frames to represent a state: note that a "frame" and a "state" are NOT the same thing
-- A "state" is an abstract representation of the game at a specific point in time. A "frame" is a video-game specific
-- term to represent one 'tick' of game time.
local STATE_FRAME_SIZE = 4

-- local variable to turn off communication with the server. Used for debugging purposes
local SEND_TO_SERVER = true

local restarting = false
local sentTerminalState = false
local clientID = generateRandomString(12)

-- memory locations, bitch
local current_loc = 0x01C044
local oneYpos_a = 0x01C070
local oneYpos_b = 0x01C074
local twoYpos_a = 0x01C078
local twoYpos_b = 0x01C07C
local ballYpos_a = 0x01C048
local ballYpos_b = 0x01C04C
local ballXpos_a = 0x01C050
local ballXpos_b = 0x01C054
local oneScore = 0x01C068
local twoScore = 0x01C06C
local countdown_timer = 0x01BFE4
local TIMER_START_VALUE = 300
local make_random = true
local high_y = 208
local low_y = 54
local total_height_of_field = high_y - low_y
random_y_vel_choices = {-0.25, -0.12, 0, 0.12, 0.25}


function make_pong_random()
    if make_random and mainmemory.read_u32_be(countdown_timer) == TIMER_START_VALUE - 1 then
        set_random_starting_vel()
        make_random = false
    elseif make_random == false and mainmemory.read_u32_be(countdown_timer) ~= TIMER_START_VALUE - 1 then
        gui.drawString(0,120, "Getting ready to add randomly!", null, null, 9)
        make_random = true
    end
end

function set_random_starting_vel()
    local value = math.random(1, #random_y_vel_choices)
    mainmemory.write_s16_be(0x01C058, random_y_vel_choices[value])
    gui.drawString(0,110, "Setting "..tostring(random_y_vel_choices[value]).." to ball's y vel", null, null, 9)
end

function waitingForBall()
    local countdown = mainmemory.read_u32_be(countdown_timer)
    if countdown < 260 then
        return true
    else
        return false
    end
end

-- For some reason, this game stores the player's y positions, and the ball's x/y coords in two different places,
-- and updates both of them in an alternating fashion (i.e. location a gets updated on frame one, location b gets updated
-- on frame 2, location a gets updated on frame 3, etc).
function get_player_1_ypos()
    local loc = mainmemory.read_u32_be(current_loc)
    if (loc == 1) then
        return mainmemory.read_u32_be(oneYpos_a)
    end
    if (loc == 0) then
        return mainmemory.read_u32_be(oneYpos_b)
    end
end

function get_player_2_ypos()
    local loc = mainmemory.read_u32_be(current_loc)
    if (loc == 1) then
        return mainmemory.read_u32_be(twoYpos_a)
    end
    if (loc == 0) then
        return mainmemory.read_u32_be(twoYpos_b)
    end
end

function get_ball_ypos()
    local loc = mainmemory.read_u32_be(current_loc)
    if (loc == 1) then
        return mainmemory.read_u32_be(ballYpos_a)
    end
    if (loc == 0) then
        return mainmemory.read_u32_be(ballYpos_b)
    end
end

function set_ball_ypos(value)
    mainmemory.write_u32_be(ballYpos_a, value)
    mainmemory.write_u32_be(ballYpos_b, value)
end

function get_ball_xpos()
    local loc = mainmemory.read_u32_be(current_loc)
    if (loc == 1) then
        return mainmemory.read_u32_be(ballXpos_a)
    end
    if (loc == 0) then
        return mainmemory.read_u32_be(ballXpos_b)
    end
end

function get_player_1_score()
    return mainmemory.read_u32_be(oneScore)
end

function get_player_2_score()
    return mainmemory.read_u32_be(twoScore)
end

-- This method adds the current frame's information to the state buffer. If the state buffer is full,
-- then the last state is popped
function add_game_state_to_state_buffer(data)
    local popped = nil
    List.pushright(currentStateBuffer, data)
    if List.length(currentStateBuffer) > STATE_FRAME_SIZE then
        popped = List.popleft(currentStateBuffer)
    end
    return popped
end

function do_debug()
    local serverAction = ""
    if (currentAction == 0) then
        serverAction = "DOWN"
    elseif (currentAction == 1) then
        serverAction = "UP"
    else
        serverAction = "CENTER"
    end

    gui.drawString(0,40, "Player 1: " .. get_player_1_ypos(), null, null, 9)
    gui.drawString(0,50, "Player 2: " .. get_player_2_ypos(), null, null, 9)
    gui.drawString(0,60, "Ball X: " .. get_ball_xpos(), null, null, 9)
    gui.drawString(0,70, "Ball Y: " .. get_ball_ypos(), null, null, 9)
    gui.drawString(0,80, "Player One Score: " .. get_player_1_score(), null, null, 9)
    gui.drawString(0,90, "Player Two Score: " .. get_player_2_score(), null, null, 9)
    gui.drawString(0,100, "Server Action: " .. serverAction, null, null, 9)
    gui.drawString(0,130, "Countdown: " .. tostring(mainmemory.read_u32_be(countdown_timer)), null, null, 9)
end

function getGameStateMap()
    local data = {}
    data["1score"] = get_player_1_score()
    data["1y"] = get_player_1_ypos()
    data["2score"] = get_player_2_score()
    data["2y"] = get_player_2_ypos()
    data["ballx"] = get_ball_xpos()
    data["bally"] = get_ball_ypos()
    return data
end

function perform_action(player, actionIndex)
    -- We are setting the analog stick to 0 for every input because, unlike buttons, we need to "unset" the analog stick
    joypad.setanalog({["X Axis"] = 0, ["Y Axis"] = 0}, 1)
    joypad.setanalog(PONG_INPUT_ORDER[actionIndex], player);
end

function game_is_over()
    return get_player_1_score() == 10 or get_player_2_score() == 10
end

function gameNeedsToRestart()
    if game_is_over() then
        return true
    else
        return false
    end
end

function game_has_loaded()
    return get_player_1_ypos() ~= nil
end

function should_send_data_to_server()
    -- If the debug flag is NOT set, then we need to first check to make sure that we have enough frames in the
    -- current state bugger. Note that a "state" is a collection of one or more frames.
    local buffersAreFull = List.length(currentStateBuffer) == STATE_FRAME_SIZE

    -- We also need to make sure that we are sending data to the server at the specified rate. For example, if the
    -- TF_SERVER_SAMPLE_SKIP_RATE equals '4', then we only send data to the server every 4 frames
    local frameIterationisDone = tfServerSampleIteration % TF_SERVER_SAMPLE_SKIP_RATE == 0

    -- Finally, we need to make sure that we only send ONE terminal state (i.e., when a player reaches 10).
    -- If the current state has one player reaching 10, and we didn't yet send data, send it.end
    local gameIsOver = get_player_1_score() == 10 or get_player_2_score() == 10
    local haventSentTerminalState = (gameIsOver == false or sentTerminalState == false)

    if buffersAreFull and frameIterationisDone and haventSentTerminalState then
        return true
    else
        return false
    end

end

-- Main scripting loop
while true do
    make_pong_random()
    restarting = gameNeedsToRestart()

    -- If the game is currently in progress, then keep training as normal. Note that we still need to send the current state when
    -- one of the players reaches 10. We just need to restart AFTER that happens.
    if ((restarting == false or sentTerminalState == false) and game_has_loaded()) then
        sentTerminalState = false -- set to false every frame to make debugging easier

        -- Gather state data and add it to our state buffer (knocking out the oldest entry)
        if waitingForBall() == false then
            local data = getGameStateMap()
            add_game_state_to_state_buffer(data)

            -- If we have all the data we need, then send data to the server
            if should_send_data_to_server() then
                if SEND_TO_SERVER then -- Set to false to fake sending to the server
                    local resp = TF_CLIENT.send_data_for_training(clientID, STATE_FRAME_SIZE, currentStateBuffer)

                    currentAction = tonumber(resp)
                end

                -- If the game is over, then indicate that we just sent a terminal state. We don't want to send another one
                -- until the game restarts
                if game_is_over() then
                    sentTerminalState = true
                end

                tfServerSampleIteration = 0

            end

            -- Do the current action we have.
            perform_action(1, currentAction)
            tfServerSampleIteration = tfServerSampleIteration + 1
        end

        do_debug()
    else
        -- Otherwise, keep pressing start until we trigger a new game
        joypad.set({["Start"] = "True" }, 1)

        -- If the game has loaded, then set the 'restarting' flag to false so that we can continue training
        if game_has_loaded() and gameNeedsToRestart() == false then
            restarting = false
        end
    end

    -- Do the next frame (and pray things don't break)
    emu.frameadvance();
end