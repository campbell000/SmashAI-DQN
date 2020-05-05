-- This file reads game states variables from memory, and sends the game state to the Learning Server.

-- This only works for the USA rom
require "global";
require "gameConstants";
require "utils";
require "list"
local TF_CLIENT = require("tensorflow-client")
local tfServerSampleIteration = 0
local currentStateBuffer = List.newList()
local currentAction = 16 -- Start off doing nothing (INPUT_ORDER[32] == CENTER NOTHING)
Game = {}

-- CONSTANTS
-- This variable is the number of frames we skip before sending / receiving data from the tf server. Note that when this
-- number is > 1, this means that the bot will HOLD down the current action N number of frames
local TF_SERVER_SAMPLE_SKIP_RATE = 4

-- This variable is the number of frames to represent a state: note that a "frame" and a "state" are NOT the same thing
-- A "state" is an abstract representation of the game at a specific point in time. A "frame" is a video-game specific
-- term to represent one 'tick' of game time.
local STATE_FRAME_SIZE = 2

-- local variable to turn off communication with the server. Used for debugging purposes
local SEND_TO_SERVER = true
local RESET_COUNTER = -1
local JUST_RESTARTED = false

local clientID = generateRandomString(12)


local prev_1_score = 0
local prev_2_score = 0
local curr_1_score = 0
local curr_2_score = 0
random_save_state = 1

savestate.loadslot(random_save_state)

function get_ball_x()
    return mainmemory.readfloat(0x0596C8, true)
end

function get_ball_y()
    return mainmemory.readfloat(0x0596CC, true)
end

function get_ball_z()
    return mainmemory.readfloat(0x0596D0, true)
end

function get_p1_x()
    return mainmemory.readfloat(0x1400A0, true)
end

function get_p1_y()
    return mainmemory.readfloat(0x1400A4, true)
end

function get_p1_z()
    return mainmemory.readfloat(0x1400A8, true)
end

function get_p2_x()
    return mainmemory.readfloat(0x1400AC, true)
end

function get_p2_y()
    return mainmemory.readfloat(0x1400B0, true)
end

function get_p2_z()
    return mainmemory.readfloat(0x1400B4, true)
end

function p1_is_serving()
    return mainmemory.read_u32_be(0x0D88CC)
end

function p2_is_serving()
    return mainmemory.read_u32_be(0x0D9054)
end

function p1_charge_level()
    return mainmemory.read_u32_be(0x157048)
end

function p2_charge_level()
    return mainmemory.read_u32_be(0x157230)
end

function receiving_player_score()
    return mainmemory.read_u32_be(0x140194)
end

function serving_player_score()
    return mainmemory.read_u32_be(0x140190)
end

function get_player_serving_for_scoring()
    return mainmemory.read_u32_be(0x246FA4)
end

function play_has_stopped()
    return mainmemory.read_u32_be(0x138004)
end

function p1_score()
    local player_serving = get_player_serving_for_scoring()
    if (player_serving == 0) then
        return serving_player_score()
    else
        return receiving_player_score()
    end
end

function p2_score()
    local player_serving = get_player_serving_for_scoring()
    if (player_serving == 1) then
        return serving_player_score()
    else
        return receiving_player_score()
    end
end

function get_ball_spin_val()
    return mainmemory.read_u32_be(0x15B1A0)
end

function get_ball_spin_type()
    local spin = mainmemory.read_u32_be(0x15B1A0)
    if spin == 0 then return "Normal Topspin"
    elseif spin == 5 then return "Normal Slice"
    elseif spin == 6 then return "Super Slice"
    elseif spin == 9 then return "Super Spike"
    elseif spin == 8 then return "Normal Spike"
    elseif spin == 2 then return "Super Topspin"
    elseif spin == 10 then return "Spike Serve"
    elseif spin == 11 then return "Slice Serve"
    elseif spin == 12 then return "Topsin Serve"
    elseif spin == 17 then return "Dropshot"
    elseif spin == 3 then return "Lob"
    end
    return tostring(spin)

end

function should_send_data_to_server(popped_frame)
    -- We need to first check to make sure that we have enough frames in the current state bugger. Note that a "state"
    -- is a collection of one or more frames.
    local buffersAreFull = List.length(currentStateBuffer) == STATE_FRAME_SIZE

    -- We also need to make sure that we are sending data to the server at the specified rate. For example, if the
    -- TF_SERVER_SAMPLE_SKIP_RATE equals '4', then we only send data to the server every 4 frames
    local frameIterationisDone = tfServerSampleIteration % TF_SERVER_SAMPLE_SKIP_RATE == 0

    if buffersAreFull and frameIterationisDone then
        return true
    else
        return false
    end
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

function get_game_state_map()
    local data = {}
    data["1srv"] = p1_is_serving()
    data["1score"] = p1_score()
    data["2srv"] = p2_is_serving()
    data["2score"] = p2_score()
    data["image"] = comm.getScreenshotAsString()
    local jrint = 0
    if JUST_RESTARTED == true then
        jrint = 1
        JUST_RESTARTED = false
    end
    data["restarted"] = jrint
    return data
end

function get_input_string()
    local string = ""
    local x = joypad.get(1)
    for k, v in pairs(x) do
        if v == true then
            string = string.." "..k
        end
    end
    string = string .. " X:"..tostring(x["X Axis"])
    string = string .. " Y:"..tostring(x["Y Axis"])
    return string
end

function do_debug()
    gui.drawString(0,20, "P1: ("..string.format("%.3f",get_p1_x())..", "..string.format("%.3f",get_p1_y())..", "..string.format("%.3f",get_p1_z())..")", null, null, 9)
    gui.drawString(0,30, "P2: ("..string.format("%.3f",get_p2_x())..", "..string.format("%.3f",get_p2_y())..", "..string.format("%.3f",get_p2_z())..")", null, null, 9)
    gui.drawString(0,40, "Ball: ("..string.format("%.3f",get_ball_x())..", "..string.format("%.3f",get_ball_y())..", "..string.format("%.3f",get_ball_z())..")", null, null, 9)
    gui.drawString(0,50, "P1 Serve: "..string.format(p1_is_serving()), null, null, 9)
    gui.drawString(0,60, "P2 Serve: "..string.format(p2_is_serving()), null, null, 9)
    gui.drawString(0,70, "P1 Charge: "..string.format(p1_charge_level()), null, null, 9)
    gui.drawString(0,80, "P2 Charge: "..string.format(p2_charge_level()), null, null, 9)
    gui.drawString(0,90, "Ball Spin: "..string.format(get_ball_spin_type()), null, null, 9)
    gui.drawString(0,100, "P1 Score: "..string.format(p1_score()), null, null, 9)
    gui.drawString(0,110, "P2 Score: "..string.format(p2_score()), null, null, 9)
    gui.drawString(0,120, "Save State: "..string.format(random_save_state), null, null, 9)
    gui.drawString(0,130, "INPUTS: "..string.format(get_input_string()), null, null, 9)
    gui.drawString(0,140, "RESET_COUNTER: "..string.format(RESET_COUNTER), null, null, 9)
    gui.drawString(0,150, "PLAY HAS STOPPED: "..string.format(play_has_stopped()), null, null, 9)


    if not should_send_data_to_server() then
        gui.drawString(0,140, "SKIPPING: ", null, null, 9)
    end
end

function perform_action(actionIndex)
    -- We are setting the analog stick to 0 for every input because, unlike buttons, we need to "unset" the analog stick
    joypad.setanalog({["X Axis"] = 0, ["Y Axis"] = 0}, 1)

    -- The given response could be a button press, a stick direction, or both. If the element corresponding to the action
    -- index has two subtables with lengths > 0, then we got a button press and a stick direction. But if the first subtable
    -- has 0 elements, then we ONLY got a stick press.
    local inputs = TENNIS_INPUT_ORDER[actionIndex]
    local firstElementLength = tablelength(inputs[1])
    if (firstElementLength >= 1) then
        joypad.set(inputs[1], 1);
    end
    joypad.setanalog(inputs[2], 1);
end

-- Do the next frame (and pray things don't break)
while true do
    joypad.setanalog({["X Axis"] = 0, ["Y Axis"] = 0}, 1)
    --do_debug()

    -- collect data
    local popped_frame = nil
    local data = nil
    if tfServerSampleIteration % 2 == 0 then
        data = get_game_state_map()
        popped_frame = add_game_state_to_state_buffer(data)
    end

    -- send to server
    if should_send_data_to_server(popped_frame) then
        if SEND_TO_SERVER then -- Set to false to fake sending to the server
            local resp = TF_CLIENT.send_data_for_training(clientID, STATE_FRAME_SIZE, currentStateBuffer)
            currentAction = tonumber(resp)
        end
        tfServerSampleIteration = 0
    end

    -- Do the current action we have.
    if SEND_TO_SERVER then
        perform_action(currentAction)
    end

    if (RESET_COUNTER == 0) then
        random_save_state = math.random(1, 4)
        savestate.loadslot(random_save_state)
        RESET_THIS_FRAME = false
        List.empty(currentStateBuffer)

        -- Without this, we'll sometimes load multiple states in a row
        curr_1_score = p1_score()
        curr_2_score = p2_score()
        prev_1_score = curr_1_score
        prev_2_score = curr_2_score
        RESET_COUNTER = -1
        JUST_RESTARTED = true
    elseif (RESET_COUNTER > 0) then
        RESET_COUNTER = RESET_COUNTER - 1
    else
        -- If someone scored, load a new state and clear the sample buffer. NOTE: we only want to do this if we're sending data
        -- on this frame
        prev_1_score = curr_1_score
        prev_2_score = curr_2_score
        curr_1_score = p1_score()
        curr_2_score = p2_score()
        if (curr_2_score > prev_2_score or curr_1_score > prev_1_score) then
            RESET_COUNTER = TF_SERVER_SAMPLE_SKIP_RATE *  2
        end
    end
    tfServerSampleIteration = tfServerSampleIteration + 1
    emu.frameadvance();
end