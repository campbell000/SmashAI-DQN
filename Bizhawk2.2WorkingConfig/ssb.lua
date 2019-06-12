-- This file reads game states variables from memory, and sends the game state to the Learning Server.

-- This only works for the USA rom
require "global";
require "gameConstants";
require "utils";
require "list"
local TF_CLIENT = require("tensorflow-client")
local X = "X Axis"
local Y = "Y Axis"
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

-- This function builds the input for the Learning Client. It includes all of the important variables of the game state
function getGameStateMap()
	local data = {}
	-- For each player, gather everything we can about their states
	for player = 1, 2 do
		data[player] = {}
		local key_prefix = tostring(player) -- prefix the keys with the current player so we can keep track of them.
		data[player]["character"] = Game.getCharacter(player) -- categorical! This needs to be one-hot encoded

		-- Get position / velocity / accel for X and Y dimensions
		local xdata = Game.getPlayerCoordinateData(player, 'x')
		local ydata = Game.getPlayerCoordinateData(player, 'y')
		data[player]["xp"] = xdata.pos
		data[player]["xv"] = xdata.vel
		data[player]["xa"] = xdata.acc
		data[player]["yp"] = ydata.pos
		data[player]["yv"] = ydata.vel
		data[player]["ya"] = ydata.acc

		-- Get movement / action states for the character
		data[player]["state"] = Game.getMovementState(player) -- categorical! This needs to be one-hot encoded!
		data[player]["shld"] = Game.getShieldSize(player)
		data[player]["shld_rec"] = Game.getShieldRecoveryTime(player)
		data[player]["jumps_remaining"] = Game.getJumpsRemaining(player)
		data[player]["direction"] = Game.getFacingDirection(player)
		data[player]["jumps"] = Game.getMovementFrame(player)
		data[player]["is_in_air"] = Game.isInAir(player)


		tf_data.append(player_data["shld"])
		tf_data.append(player_data["shld_rec"])
		tf_data.append(player_data["dir"])
		tf_data.append(player_data["jumps"])
		tf_data.append(player_data["dmg"])
		tf_data.append(player_data["state"])
		tf_data.append(player_data["is_air"])


		-- Finally, get current damage
		data[player]["damage"] = Game.getDamage(player)
	end

	-- TODO: do this better
	-- With the current state, record the action that we took during the previous state
	data[1]["prev_action_taken"] = previousAction

	return data
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

-- This method applies the button presses to the game
function do_button_presses(inputs, player)
	-- We are setting the analog stick to 0 for every input because, unlike buttons, we need to "unset" the analog stick
	joypad.setanalog({["X Axis"] = 0, ["Y Axis"] = 0}, 1)

	local button = inputs[1]
	local analog = inputs[2]

	joypad.set(button, player);
	joypad.setanalog(analog, player);
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

	-- Do not ask for inputs or send data to train if we're reviving or we just died last frame. In fact, clear the state buffer.
	if Game.getMovementState(1) == 7 or (popped_frame ~= nil and popped_frame[1]["state"] <= 4) then
		local a
	elseif List.length(currentStateBuffer) == STATE_FRAME_SIZE and tfServerSampleIteration % TF_SERVER_SAMPLE_SKIP_RATE == 0 then
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

	dumpPlayerInfo(1)
end