-- This only works for the USA rom
require ".global";
require ".gameConstants";

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

while true do
    dumpPlayerInfo(1);
	emu.frameadvance();
end