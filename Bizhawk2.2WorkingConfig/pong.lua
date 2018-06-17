-- This file reads game states variables from memory, and sends the game state to the Learning Server.

-- This only works for the USA rom
require "global";
require "gameConstants";
require "utils";
require "list"
local TF_CLIENT = require("tensorflow-client")
local tfServerSampleIteration = 0
local previousStateBuffer = List.newList()
local currentStateBuffer = List.newList()
local currentAction = INPUTS.CENTER_NOTHING
local previousAction = "9"
Game = {}

-- CONSTANTS
-- This variable is the number of frames we skip before sending / receiving data from the tf server. Note that when this
-- number is > 1, this means that the bot will HOLD down the current action N number of frames
local TF_SERVER_SAMPLE_SKIP_RATE = 2

-- This variable is the number of frames to represent a state: note that a "frame" and a "state" are NOT the same thing
-- A "state" is an abtract representation of the game at a specific point in time. A "frame" is a video-game specific
-- term to represent one 'tick' of game time.
local STATE_FRAME_SIZE = 2


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

-- This method parses the response from the Learning Server into button presses.
function parse_server_response_into_inputs(resp)
    local tokens = split(resp, ",")
    for i = 1, #tokens do
        if tokens[i] == "1" then
            input = INPUT_ORDER[i]
            if input == nil then
                print("WE DIDNT GET A VALID ACTION! SOMETHING IS WRONG!")
            end
            return input
        end
    end
    print("WE GOT A RESPONSE FROM THE SERVER WITHOUT AN ACTION! SOMETHING IS WRONG!")
end

-- This method adds the current frame's information to the state buffer. If the state buffer is full,
-- then the last state is popped (before that, we assign the previousStateBuffer as the value in
-- currentStateBuffer).
function add_game_state_to_state_buffer(data)
    local popped = nil
    List.pushright(currentStateBuffer, data)
    if List.length(currentStateBuffer) > STATE_FRAME_SIZE then
        popped = List.popleft(currentStateBuffer)
    end
    return popped
end

-- Main scripting loop
while true do
    -- Gather state data and add it to our state buffer (knocking out the oldest entry)
    local data = getGameStateMap()
    local popped_frame = add_game_state_to_state_buffer(data)

    if List.length(currentStateBuffer) == STATE_FRAME_SIZE and tfServerSampleIteration % TF_SERVER_SAMPLE_SKIP_RATE == 0 then
        -- If we have all the states we need both buffers (previous and current), and we're not skipping this frame, then get our inputs from the server
        if List.length(previousStateBuffer) == STATE_FRAME_SIZE  then
            local resp = TF_CLIENT.send_data_for_training(STATE_FRAME_SIZE, currentStateBuffer, previousStateBuffer)
            currentAction = parse_server_response_into_inputs(resp)
            tfServerSampleIteration = 0

            -- Record the fact that, for the current frame, we executed a specific action. This will be used by the server
            -- the next time that we send data.
            previousAction = currentAction
        end

        -- The previous state buffer needs to represent what we sent to the TF server LAST time we talked to it
        previousStateBuffer = List.copy(currentStateBuffer)
    end

    -- Do the current action we have.
    do_button_presses(currentAction, 1)

    -- Do the next frame (and pray things don't break)
    emu.frameadvance();

    tfServerSampleIteration = tfServerSampleIteration + 1
end