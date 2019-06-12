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

-- This function returns the player
function Game.getPlayer(player)
    if type(player) ~= "number" or player == 1 then
        return dereferencePointer(GameConstants.Memory.player_list_pointer);
    end
    local playerList = dereferencePointer(GameConstants.Memory.player_list_pointer);
    if isRDRAM(playerList) then
        return playerList + (player - 1) * 0xB50;
    end
end

-- This function returns the numerical representation of the player's character
function Game.getCharacter(player)
    local playerActor = Game.getPlayer(player);
    if isRDRAM(playerActor) then
        return mainmemory.readbyte(playerActor + GameConstants.player_fields.Character);
    end
    return 0x1c
end

-- This function returns the String representation of the player's character (ex: Yoshi)
function Game.getCharacterName(player)
    character_byte_value = Game.getCharacter(player);
    if (keyExists(GameConstants.characters, character_byte_value)) then
        return GameConstants.characters[character_byte_value]
    end
    return "None"
end

-- This function returns the numerical representation of the player's current state ("standing", "attacking", etc)
function Game.getMovementState(player)
    local playerActor = Game.getPlayer(player);
    if isRDRAM(playerActor) then
        return mainmemory.read_u16_be(playerActor + GameConstants.player_fields.MovementState);
    end
    return 0;
end

-- This function returns the frame number of the player's current action. For example, if an attack lasts 31 frames,
-- this method will return 0-31
function Game.getMovementFrame(player)
    local playerActor = Game.getPlayer(player);
    if isRDRAM(playerActor) then
        return mainmemory.read_u32_be(playerActor + GameConstants.player_fields.MovementFrame);
    end
    return 0;
end

-- This method returns 1 if the character is facing right, -1 if the character is facing left
function Game.getFacingDirection(player)
    local playerActor = Game.getPlayer(player);
    if isRDRAM(playerActor) then
        return mainmemory.read_s32_be(playerActor + GameConstants.player_fields.FacingDirection);
    end
    return 0
end

function Game.getMovementString(player)
    local movementState = Game.getMovementState(player);
    if type(GameConstants.movement_states[movementState]) == "string" then
        return GameConstants.movement_states[movementState];
    else
        local characterIndex = Game.getCharacter(player);
        if type(GameConstants.character_states[characterIndex]) == "table" and type(GameConstants.character_states[characterIndex][movementState]) == "string" then
            return GameConstants.character_states[characterIndex][movementState];
        end
    end
    return "Unknown "..tostring(movementState);
end

-- Returns a dict that contains the position, velocity, and acceleration of the
-- given player. The keys are "pos", "vel", and "acc".
-- Args: pass in player number and a dimension ('x', 'y', or 'z')
function Game.getPlayerCoordinateData(player, dimension)
    local POS = "pos"
    local VEL = "vel"
    local ACC = "acc"

    -- initialize the return values to 0 in case there's no fighting going on in the main game (menus, etc).
    local data = {
        [POS] = 0,
        [VEL] = 0,
        [ACC] = 0
    };

    -- initialize the values to get the velocity, position, and acceleration based on the dimension arguments
    local posIndex = "XPosition"
    local velIndex = "XVelocity"
    local accIndex = "XAcceleration"
    if (dimension == 'y') then
        posIndex = "YPosition"
        velIndex = "YVelocity"
        accIndex = "YAcceleration"
    elseif (dimension == 'z') then
        posIndex = "ZPosition"
        velIndex = "ZVelocity"
        accIndex = "ZAcceleration"
    end

    local playerActor = Game.getPlayer(player);
    if isRDRAM(playerActor) then
        local positionData = dereferencePointer(playerActor + GameConstants.player_fields.PositionDataPointer);
        if isRDRAM(positionData) then
            data[POS] = mainmemory.readfloat(positionData + GameConstants.player_fields.PositionData[posIndex], true)
            data[VEL] = mainmemory.readfloat(playerActor + GameConstants.player_fields[velIndex], true)
            data[ACC] = mainmemory.readfloat(playerActor + GameConstants.player_fields[accIndex], true)
        end
    end
    return data;
end

-- This method returns the number of jumps remaining for the given player
function Game.getJumpsRemaining(player)
    local playerActor = Game.getPlayer(player);
    if isRDRAM(playerActor) then
        local curr_jumps =  mainmemory.readbyte(playerActor + GameConstants.player_fields.JumpCounter);
        local characterConstants = dereferencePointer(playerActor + GameConstants.player_fields.CharacterConstantsPointer);
        local NumberOfJumps = mainmemory.read_u32_be(characterConstants + GameConstants.player_fields.CharacterConstants.NumberOfJumps)
        return NumberOfJumps - curr_jumps
    end
    return 0;
end

-- This method returns the player's current shield size (i.e. shield health)
function Game.getShieldSize(player)
    local playerActor = Game.getPlayer(player);
    if isRDRAM(playerActor) then
        return mainmemory.read_s32_be(playerActor + GameConstants.player_fields.ShieldSize);
    end
    return 0;
end

function Game.getShieldRecoveryTime(player)
    local playerActor = Game.getPlayer(player);
    if isRDRAM(playerActor) then
        return mainmemory.read_s32_be(playerActor + GameConstants.player_fields.ShieldBreakerRecoveryTimer);
    end
    return 0;
end

function Game.getDamage(player)
    local matchSettings = dereferencePointer(GameConstants.Memory.match_settings_pointer)
    local damageAddr = matchSettings + GameConstants.match_settings.player_base[player]
    damageAddr = damageAddr	+ GameConstants.match_settings.player_data.damage
    return mainmemory.read_s32_be(damageAddr)
end

function Game.isInAir(player)
    local playerActor = Game.getPlayer(player);
    if isRDRAM(playerActor) then
        return mainmemory.read_u32_be(playerActor + GameConstants.player_fields.Grounded)
    end
end

function dumpPlayerInfo(player)
    gui.drawString(0,0, "Character: " .. Game.getCharacterName(player), null, null, 9)

    -- Dump position, velocity for X, Y, and Z coordinates
    local xData = Game.getPlayerCoordinateData(player, 'x')
    local yData = Game.getPlayerCoordinateData(player, 'y')
    local zData = Game.getPlayerCoordinateData(player, 'z')
    gui.drawString(0,10, "X: " .. xData.pos .. "," .. xData.vel .. "," .. xData.acc, null, null, 9)
    gui.drawString(0,20, "Y: " .. yData.pos .. "," .. yData.vel .. "," .. yData.acc, null, null, 9)
    gui.drawString(0,30, "Z: " .. zData.pos .. "," .. zData.vel .. "," .. zData.acc, null, null, 9)

    -- Get the various states of the characters
    gui.drawString(0,40, "State: " .. Game.getMovementString(player), null, null, 9)
    gui.drawString(0,50, "Shield Size (Recovery Timer): " .. Game.getShieldSize(player) .. "(" .. Game.getShieldRecoveryTime(player) .. ")", null, null, 9)
    gui.drawString(0,60, "Dir Facing: " .. Game.getFacingDirection(player), null, null, 9)
    gui.drawString(0,70, "Jump Counter: " .. Game.getJumpsRemaining(player), null, null, 9)
    gui.drawString(0,80, "Damage%: " .. Game.getDamage(player), null, null, 9)
    gui.drawString(0,90, "In In Air: " .. Game.isInAir(player), null, null, 9)
end

function perform_action(player, actionIndex)
    -- We are setting the analog stick to 0 for every input because, unlike buttons, we need to "unset" the analog stick
    joypad.setanalog({["X Axis"] = 0, ["Y Axis"] = 0}, 1)

    -- The given response could be a button press, a stick direction, or both. If the element corresponding to the action
    -- index has two subtables with lengths > 0, then we got a button press and a stick direction. But if the first subtable
    -- has 0 elements, then we ONLY got a stick press.
    local inputs = INPUT_ORDER[actionIndex]
    local firstElementLength = tablelength(inputs[1])
    if (firstElementLength == 1) then
        joypad.set(inputs[1], player);
    end
    joypad.setanalog(inputs[2], player);
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

function should_send_data_to_server(popped_frame)
    -- We need to first check to make sure that we have enough frames in the current state bugger. Note that a "state"
    -- is a collection of one or more frames.
    local buffersAreFull = List.length(currentStateBuffer) == STATE_FRAME_SIZE

    -- We also need to make sure that we are sending data to the server at the specified rate. For example, if the
    -- TF_SERVER_SAMPLE_SKIP_RATE equals '4', then we only send data to the server every 4 frames
    local frameIterationisDone = tfServerSampleIteration % TF_SERVER_SAMPLE_SKIP_RATE == 0

    -- Finally, don't sne data to the server if we're respawning or already sent a terminal state to the server (we died).
    --
    local isDeadOrRespawning = Game.getMovementState(1) == 7 or (popped_frame ~= nil and popped_frame[1]["state"] <= 4)

    if buffersAreFull and frameIterationisDone and isDeadOrRespawning then
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

    if buffersAreFull and frameIterationisDone and gameIsOver then
        return true
    else
        return false
    end
end

function convertServerResponseToAction(resp)
    -- We're adding one because the INPUT_ORDER array starts at 1 (as do normal lua arrays), but server response starts
    -- at 0!
    local currentAction = tonumber(resp)
    currentAction = currentAction + 1
    return currentAction
end

-- Main scripting loop
while true do
    -- Gather state data and add it to our state buffer (knocking out the oldest entry)
    local data = getGameStateMap()
    add_game_state_to_state_buffer(data)

    -- If we have all the data we need, then send data to the server
    if should_send_data_to_server() then
        if SEND_TO_SERVER then -- Set to false to fake sending to the server
            local resp = TF_CLIENT.send_data_for_training(clientID, STATE_FRAME_SIZE, currentStateBuffer)
            currentAction = convertServerResponseToAction(resp)
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

    -- print some shit on the screen
    do_debug()

    -- Do the next frame (and pray things don't break)
    emu.frameadvance();
end