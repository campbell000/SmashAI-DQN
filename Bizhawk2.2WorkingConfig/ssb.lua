-- This only works for the USA rom
require "global";
require "gameConstants";
local TF_CLIENT = require("tensorflow-client")
local X = "X Axis"
local Y = "Y Axis"
Game = {}

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

function Game.getCharacter(player)
	local playerActor = Game.getPlayer(player);
	if isRDRAM(playerActor) then
		return mainmemory.readbyte(playerActor + GameConstants.player_fields.Character);
	end
	return 0x1c
end

function Game.getCharacterName(player)
	character_byte_value = Game.getCharacter(player);
	if (keyExists(GameConstants.characters, character_byte_value)) then
	    return GameConstants.characters[character_byte_value]
	end
	return "None"
end

function Game.getMovementState(player)
	local playerActor = Game.getPlayer(player);
	if isRDRAM(playerActor) then
		return mainmemory.read_u16_be(playerActor + GameConstants.player_fields.MovementState);
	end
	return 0;
end

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
end

-- This function builds the input
function buildDataMapForServer()
	local data = {}
	-- For each player, gather everything we can about their states
	for player = 1, 2 do
		local key_prefix = tostring(player) -- prefix the keys with the current player so we can keep track of them.
		data[key_prefix.."character"] = Game.getCharacter(player) -- categorical! This needs to be one-hot encoded

		-- Get position / velocity / accel for X and Y dimensions
		local xdata = Game.getPlayerCoordinateData(player, 'x')
		local ydata = Game.getPlayerCoordinateData(player, 'y')
		data[key_prefix.."xp"] = xdata.pos
		data[key_prefix.."xv"] = xdata.vel
		data[key_prefix.."xa"] = xdata.acc
		data[key_prefix.."yp"] = ydata.pos
		data[key_prefix.."yv"] = ydata.vel
		data[key_prefix.."ya"] = ydata.acc

		-- Get movement / action states for the character
		data[key_prefix.."state"] = Game.getMovementState(player) -- categorical! This needs to be one-hot encoded!
		data[key_prefix.."shield_size"] = Game.getShieldSize(player)
		data[key_prefix.."shield_recovery_time"] = Game.getShieldRecoveryTime(player)
		data[key_prefix.."direction"] = Game.getFacingDirection(player)
		data[key_prefix.."jumps_remaining"] = Game.getJumpsRemaining(player)
	end
	return data
end

function split(inputstr, sep)
	if sep == nil then
		sep = "%s"
	end
	local t={} ; i=1
	for str in string.gmatch(inputstr, "([^"..sep.."]+)") do
		t[i] = str
		i = i + 1
	end
	return t
end

function dump(o)
	if type(o) == 'table' then
		local s = '{ '
		for k,v in pairs(o) do
			if type(k) ~= 'number' then k = '"'..k..'"' end
			s = s .. '['..k..'] = ' .. dump(v) .. ','
		end
		return s .. '} '
	else
		return tostring(o)
	end
end

function parse_server_response_into_inputs(resp)
	local buttons = {}
	local analogs = {}
	local r = {}
	local tokens = split(resp, ",")
	for i = 1, #tokens do
		if tokens[i] == "1" then
			if i <= 5 then
				buttons[BUTTONS[i]] = "True"
			else
				local analog_vals = ANALOG_VALS[i]
				x_val = analog_vals["X"]
				y_val = analog_vals["Y"]

				if x_val ~= nil then
					analogs[X] = x_val
				end

				if y_val ~= nil then
					analogs[Y] = y_val
				end
			end
		end
	end

	r[1] = buttons
	r[2] = analogs
	return r
end

while true do
	-- Gather state data, send it to the server, and wait for the server's response (which should be inputs)
    data = buildDataMapForServer()
	resp = TF_CLIENT.say_hello(data)

	-- We expect (in string form) a comma-separated list of 0's and 1's, where 1 indicates that the button should be pressed.
	-- We need to parse the string into a lua table and feed it into Bizhawk as inputs
	inputs = parse_server_response_into_inputs(resp)
	joypad.set(inputs[1], 1);
	joypad.setanalog(inputs[2], 1);

	emu.frameadvance();
end