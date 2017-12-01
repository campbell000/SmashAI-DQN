-- This file contains game related constants. The majority of these constants were taken
-- from https://github.com/Isotarge/ScriptHawk/blob/master/games/smash64.lua
N64 = {
	RDRAMBase = 0x80000000;
	RDRAMSize = 0x800000; -- Halved with no expansion pak, can be read from 0x80000318
}

GameConstants = {
	speedy_speeds = { .1, 1, 5, 10, 20, 35, 50, 75, 100 };
	speedy_index = 6;
	max_rot_units = 4,
	Memory = {
		["music"] = 0x99113,
		["unlocked_stuff"] = 0xA4934,
		["match_settings_pointer"] = 0xA50E8,
		["hurtbox_color_RG"] =  0xF2786,
		["hurtbox_color_BA"] = 0xF279E,
		["red_hitbox_patch"] = 0xF33BC,
		["purple_hurtbox_patch"] = 0xF2FD0,
		["player_list_pointer"] = 0x130D84,
		["item_list_pointer"] = 0x46700,
		["item_hitbox_offset"] = 0x374,
	},
	characters = {
		[0x00] = "Mario",
		[0x01] = "Fox",
		[0x02] = "DK",
		[0x03] = "Samus",
		[0x04] = "Luigi",
		[0x05] = "Link",
		[0x06] = "Yoshi",
		[0x07] = "Falcon",
		[0x08] = "Kirby",
		[0x09] = "Pikachu",
		[0x0A] = "Jigglypuff",
		[0x0B] = "Ness",
		[0x0C] = "Master Hand",
		[0x0D] = "Metal Mario",
		[0x0E] = "Polygon Mario",
		[0x0F] = "Polygon Fox",
		[0x10] = "Polygon DK",
		[0x11] = "Polygon Samus",
		[0x12] = "Polygon Luigi",
		[0x13] = "Polygon Link",
		[0x14] = "Polygon Yoshi",
		[0x15] = "Polygon Falcon",
		[0x16] = "Polygon Kirby",
		[0x17] = "Polygon Pikachu",
		[0x18] = "Polygon Jigglypuff",
		[0x19] = "Polygon Ness",
		[0x1A] = "Giant DK",
		--[0x1B] = "Crash",
		[0x1C] = "None", -- No character selected
	},
	match_settings = {
		map = 0x01, -- Byte
		match_type = 0x03, -- Byte (bitfield?) Values: 0x01 = time, 0x02 = stock, 0x03 = timed stock match
		time = 0x06, -- Byte
		stock = 0x07, -- Byte
		player_base = {
			[1] = 0x20,
			[2] = 0x94,
			[3] = 0x108,
			[4] = 0x17C,
		},
		player_data = { -- Relative to player_base[player]
			controlled_by = 0x02, -- Byte: 0 Human, 1 AI, 2 None
			character = 0x03, -- Byte
			damage = 0x4C, -- u32_be, Only applies to the UI, real damage is stored in the player object
		}
	},
	movement_states = {
		[0x00] = "Dying (Down)", [0x01] = "Dying (Side)", [0x02] = "Dying (Up far)", [0x03] = "Dying (Up near)", [0x05] = "Appearing",
		[0x07] = "Reviving", [0x08] = "Spawning", [0x09] = "Standing on Spawning Platform",
		[0x0A] = "Standing", [0x0B] = "Walking slowly", [0x0C] = "Walking", [0x0D] = "Walking quickly",
		[0x0F] = "Initial Dash", [0x10] = "Running", [0x11] = "Running (End)",
		[0x12] = "Switching direction", [0x13] = "Switching Running direction",
		[0x14] = "Jumping (Start)", [0x15] = "Shield Jumping", [0x16] = "Jumping +YVel",
		[0x17] = "Jumping Backwards", [0x18] = "Air Jumping", [0x19] = "Air Jumping Backwards",
		[0x1A] = "Jumping -YVel", [0x1B] = "Air Jumping while -YVel",
		[0x1C] = "Crouching (Start)", [0x1D] = "Crouching", [0x1E] = "Crouching (End)",
		[0x1F] = "Landing", [0x20] = "Landing hardly",
		[0x21] = "Dropping through platform", [0x22] = "Shield Dropping through platform",
		[0x23] = "Teeter", [0x24] = "Teeter (Start)",
		[0x25] = "Damaged (No Down)", [0x26] = "Damaged (No Down)", [0x27] = "Damaged (No Down)",
		[0x28] = "Damaged (No Down)", [0x29] = "Damaged (No Down)", [0x2A] = "Damaged (No Down)",
		[0x2B] = "Damaged", [0x2C] = "Damaged", [0x2D] = "Damaged", [0x2E] = "Damaged", [0x2F] = "Damaged",
		[0x30] = "Damaged", [0x31] = "Damaged", [0x32] = "Damaged", [0x33] = "Damaged", [0x34] = "Damaged",
		[0x35] = "Damaged", [0x36] = "Damaged", [0x37] = "Damaged", [0x38] = "Damaged",
		[0x39] = "End of Stun",
		[0x3A] = "Falling After Up-Special (Aerial)", [0x3B] = "Landing after Up-Special (Aerial)",
		[0x3C] = "Damaged (Tornado)", [0x3D] = "Getting into the Barrel",
		[0x3E] = "Entering the Pipe", [0x3F] = "Moving inside the Pipe", [0x40] = "Coming out of the Pipe", [0x41] = "Coming out of the Abyth",
		[0x42] = "Bonk Ceiling",
		[0x43] = "Facedown N Down", [0x44] = "Faceup N Down", [0x45] = "Facedown Downed", [0x46] = "Faceup Downed",
		[0x47] = "Getting Recovery from Facedown Down", [0x48] = "Getting Recovery from Faceup Down",
		[0x49] = "Forwards Teching", [0x4A] = "Backwards Teching",
		[0x4B] = "Rolling Forwards from Facedown Down", [0x4C] = "Rolling Forwards from Faceup Down",
		[0x4D] = "Rolling Backwards from Faceup Down", [0x4E] = "Rolling Backwards from Faceup Down",
		[0x4F] = "Attack from Facedown Down", [0x50] = "Attack from Faceup Down", [0x51] = "Teching",
		[0x54] = "Grabbing Edge (Start)", [0x55] = "Grabbing Edge",
		[0x56] = "Rising Edge (Start)", [0x57] = "Rising Edge", [0x58] = "Rising Edge (End)",
		[0x59] = "Rising Edge (100%) (Start)", [0x5A] = "Rising Edge (100%)", [0x5B] = "Rising Edge (100%) (End)",
		[0x5C] = "Edge Attack (Start)", [0x5D] = "Edge Attack",
		[0x5E] = "Edge Attack (100%) (Start)", [0x5F] = "Edge Attack (100%)",
		[0x60] = "Edge Rolling (Start)", [0x61] = "Edge Rolling",
		[0x62] = "Edge Rolling (100%) (Start)", [0x63] = "Edge Rolling (100%)", [0x64] = "Getting an Item",
		[0x65] = "Picking up an Item", [0x66] = "Holding an Item", [0x67] = "Switching Direction During Holding an Item",
		[0x68] = "Throw", [0x69] = "Dash Throw", [0x6A] = "Forward Throw", [0x6B] = "Back Throw", [0x6C] = "Up Throw", [0x6D] = "Down Throw",
		[0x6E] = "Forward Throw(Smash)", [0x6F] = "Back Throw(Smash)", [0x70] = "Up Throw (Smash)", [0x71] = "Down Throw (Smash)",
		[0x72] = "Throw-Air", [0x73] = "Back Throw-Air", [0x74] = "Up Throw-Air", [0x75] = "Down Throw-Air",
		[0x76] = "Throw-Air (Smash)", [0x77] = "Back Throw-Air (Smash)", [0x78] = "Up Throw-Air (Smash)", [0x79] = "Down Throw-Air (Smash)",
		[0x7E] = "Beam Sword (Jab)", [0x7F] = "Beam Sword (Tilt)", [0x80] = "Beam Sword (Smash)", [0x81] = "Beam Sword (Dash)",
		[0x7A] = "Crate Throw", [0x7B] = "Reverse Crate Throw", [0x7C] = "Crate Throw (Smash)", [0x7D] = "Reverse Crate Throw (Smash)",
		[0x82] = "Home-Run Bat (Jab)", [0x83] = "Home-Run Bat (Tilt)", [0x84] = "Home-Run Bat (Smash)", [0x85] = "Home-Run Bat (Dash)",
		[0x86] = "Harisen (Jab)", [0x87] = "Harisen (Tilt)", [0x88] = "Harisen (Smash)", [0x89] = "Harisen (Dash)",
		[0x8A] = "Star Rod (Jab)", [0x8B] = "Star Rod (Tilt)", [0x8C] = "Star Rod (Smash)", [0x8D] = "Star Rod (Dash)",
		[0x8E] = "Ray Gun", [0x8F] = "Ray Gun (Aerial)", [0x90] = "Fire Flower", [0x91] = "Fire Flower (Aerial)",
		[0x92] = "Hammer (Stand)", [0x93] = "Hammer (Walk)", [0x94] = "Hammer (Switch)",
		[0x95] = "Hammer (Jump)", [0x96] = "Hammer (Air)", [0x97] = "Hammer (Land)",
		[0x98] = "Shield (Start)", [0x99] = "Shield", [0x9A] = "Shield (End)",
		[0x9B] = "Stunned During Shield",
		[0x9C] = "Rolling Forwards", [0x9D] = "Rolling Backwards",
		[0x9E] = "Shield Breaking",
		[0xA1] = "SB Downed", [0xA3] = "SB Stunned (Start)", [0xA4] = "SB Stunned", [0xA5] = "Sleeping",
		[0xA6] = "Grab", [0xA7] = "Grabbing (Start)", [0xA8] = "Grabbing", [0xA9] = "Throwing", [0xAA] = "Back Throwing",
		[0xAB] = "Getting Grabbed (Start)", [0xAC] = "Getting Grabbed",
		[0xAD] = "Getting Vacuumed", [0xAE] = "Getting Stuffed", [0xAF] = "Getting Spat", [0xB0] = "Getting Copied",
		[0xB1] = "Getting Tongue", [0xB2] = "Being Egg",
		[0xB3] = "Getting FalconDive",
		[0xB5] = "Getting Mounted (Start)", [0xB8] = "Getting Mounted",
		[0xBA] = "Getting Grabbed (End)", [0xBB] = "Getting Grabbed (End)",
		[0xBD] = "Taunt", [0xBE] = "Jab 1", [0xBF] = "Jab 2",
		[0xC0] = "Dash Attack",
		[0xC1] = "Forward Tilt (high)", [0xC2] = "Forward Tilt (mid-high)", [0xC3] = "Forward Tilt", [0xC4] = "Forward Tilt (mid-low)", [0xC5] = "Forward Tilt (low)",
		[0xC7] = "Up Tilt", [0xC9] = "Down Tilt",
		[0xCA] = "Forward Smash (high)", [0xCB] = "Forward Smash (mid-high)", [0xCC] = "Forward Smash", [0xCD] = "Forward Smash (mid-low)", [0xCE] = "Forward Smash (low)",
		[0xCF] = "Up Smash", [0xD0] = "Down Smash",
		[0xD1] = "Neutral Air", [0xD2] = "Forward Air", [0xD3] = "Back Air", [0xD4] = "Up Air", [0xD5] = "Down Air",
		[0xD7] = "Forward Air Landing", [0xD8] = "Backward Air Landing", [0xD9] = "Miss Landing",
		[0xDA] = "Miss Landing hardly", [0xDB] = "Miss Landing softly",
	};
	player_fields = {
		["Character"] = 0x0B, -- Byte?
		["Costume"] = 0x10, -- Byte?
		["MovementFrame"] = 0x1C, -- u32_be
		["MovementState"] = 0x26, -- u16_be
		--0x2C = Health (2 Bytes)
		["ShieldSize"] = 0x34, -- s32_be
		["FacingDirection"] = 0x44, -- s32_be -- -1 = left, 1 = right
		["XVelocity"] = 0x48, -- Float
		["YVelocity"] = 0x4C, -- Float
		["ZVelocity"] = 0x50, -- Float
		["XAcceleration"] = 0x60, -- Float
		["YAcceleration"] = 0x64, -- Float
		["ZAcceleration"] = 0x68, -- Float
		["PositionDataPointer"] = 0x78, -- Pointer
		["PositionData"] = {
			["XPosition"] = 0x00, -- Float
			["YPosition"] = 0x04, -- Float
			["ZPosition"] = 0x08, -- Float
		},
		["JumpCounter"] = 0x148, -- Byte
		["Grounded"] = 0x14C, -- Byte
		["ControllerInputPointer"] = 0x1B0,
		["ShieldBreakerRecoveryTimer"] = 0x26C, -- s32_be
		--0x39C = Something to do with Attack Hitbox (4 Bytes)
		["InvinvibilityState"] = 0x5AC, -- u16_be
		["hurtbox_lower_Stomach"] = 0x5BC,
		["hurtbox_head"] = 0x5E8,
		["hurtbox_upper_right_arm"] = 0x614,
		["hurtbox_upper_right_arm"] = 0x640,
		["hurtbox_upper_left_arm"] = 0x66C,
		["hurtbox_lower_right_arm"] = 0x698,
		["hurtbox_lower_left_arm"] = 0x6C4,
		["hurtbox_upper_right_leg"] = 0x6F0,
		["hurtbox_upper_left_leg"] = 0x71C,
		["hurtbox_lower_right_leg"] = 0x748,
		["hurtbox_lower_left_leg"] = 0x774,
		hurtbox = {
			state = 0x00, -- 4 bytes
			id = 0x04, -- 4 bytes
			pointer = 0x08, -- 4 bytes
			x_position = 0x14, -- Float
			y_position = 0x18, -- Float
			z_position = 0x1C, -- Float
			width = 0x20, -- Float
			length = 0x24, -- Float
			height = 0x28, -- Float
		},
		["CharacterConstantsPointer"] = 0x9C8,
		["CharacterConstants"] = {
			["BodySizeMultiplier"] = 0x00, -- Float
			--0x04 = Unknown Float
			--0x08 = Unknown Float
			--0x0C = Unknown Float
			--0x1C = Unknown Float
			["WalkSpeedMultiplier"] = 0x20, -- Float [Usually Multiplies with 80]
			["BrakeForce"] = 0x24, -- Float
			["InitialDashSpeed"] = 0x28, -- Float
			["DashDeceleration"] = 0x2C, -- Float
			["RunningSpeed"] = 0x30, -- Float
			["JumpFrameDelay"] = 0x34, -- Float
			--0x38 = Starting X-Air Velocity Multiplier after moving before 1st jump (Multiplied by 80)
			["JumpHeightMultiplier"] = 0x3C, -- Float
			["JumpHeight"] = 0x40, -- Float
			--0x44 = Starting X-Air Velocity Multiplier after moving before 2nd jump (Multiplied by 80)
			["SecondJumpMultiplier"] = 0x48, -- Float
			["XAirAcceleration"] = 0x4C, -- Float
			["XAirMaximumSpeed"] = 0x50, -- Float
			["XAirResistance"] = 0x54, -- Float
			["YFallAcceleration"] = 0x58, -- Float
			["TerminalVelocity"] = 0x5C, -- Float
			["TerminalVelocity_FastFall"] = 0x60, -- Float
			["NumberOfJumps"] = 0x64,
			["Weight"] = 0x68, -- Float
			["SmallComboConnection"] = 0x6C, -- Float
			["DashToRunConnection"] = 0x70, -- Float
			["ShieldRadius"] = 0x74, -- Float
		},
		["CameraZoom"] = 0x864, -- Float
		-- 0xA28 = Flash State Pointer? (Pointer)
		-- 0xA2B = Flash State Index? (Byte)
		-- 0xA68 = Flash Color Red (Byte)
		-- 0xA69 = Flash Color Green (Byte)
		-- 0xA6A = Flash Color Blue (Byte)
		-- 0xA6B = Flash Color Alpha (Byte)
		["BoomerangPointer"] = 0xADC, -- Pointer
		["ShieldJump_FrameDelayCounter"] = 0xB1C, -- 4 Bytes
		["ShowHitbox"] = 0xB4C, -- u32_be
	};
	character_states = {
	[0x00] = { -- Mario
		[0xDC] = "Jab 3",
		[0xDE] = "Appearing",
		[0xDF] = "Fireball", [0xE0] = "Fireball (Aerial)",
		[0xE1] = "Up-Special", [0xE2] = "Up-Special (Aerial)",
		[0xE3] = "Down-Special", [0xE4] = "Down-Special (Aerial)",
	},
	[0x01] = { -- Fox
		[0xDC] = "Jab Loop (Start)", [0xDD] = "Jab Loop", [0xDE] = "Jab Loop (End)",
		[0xDF] = "Appearing", [0xE0] = "Arwing",
		[0xE1] = "Laser", [0xE2] = "Laser (Aerial)",
		[0xE3] = "Fire Fox (Start)", [0xE4] = "Fire Fox (Aerial) (Start)",
		[0xE5] = "Readying Fire Fox", [0xE6] = "Readying Fire Fox (Aerial)",
		[0xE7] = "Fire Fox", [0xE8] = "Fire Fox (Aerial)",
		[0xE9] = "Fire Fox (End)", [0xEA] = "Fire Fox (Aerial) (End)",
		[0xEB] = "Landing while Fire Fox (Aerial)",
		[0xEC] = "Shine (Start)", [0xED] = "Reflecting", [0xEE] = "Shine (End)", [0xEF] = "Shine",
		[0xF0] = "Switching Direction Shine",
		[0xF1] = "Shine (Aerial) (Start)", [0xF3] = "Shine (Aerial) (End)", [0xF4] = "Shine (Aerial)",
		[0xF5] = "Switching Direction Shine (Aerial)",
	},
	[0x02] = { -- DK
		[0xDD] = "Appearing",
		[0xDE] = "Charge (Start)", [0xDF] = "Charge (Aerial) (Start)",
		[0xE0] = "Charging", [0xE1] = "Charging (Aerial)",
		[0xE2] = "Punching", [0xE3] = "Punching (Aerial)",
		[0xE4] = "Maximum Punching", [0xE5] = "Maximum Punching (Aerial)",
		[0xE6] = "Up-Special", [0xE7] = "Up-Special (Aerial)",
		[0xE8] = "Down-Special (Start)", [0xE9] = "Down-Special", [0xEA] = "Down-Special (End)",
		[0xEB] = "Standing (Mounting)",
		[0xEC] = "Walking slowly (Mounting)", [0xED] = "Walking (Mounting)", [0xEE] = "Walking quickly (Mounting)",
		[0xEF] = "Switching direction (Mounting)",
		[0xF0] = "Jump (Mounting) (Start)", [0xF1] = "Jumping (Mounting)", [0xF2] = "Landing (Mounting)",
		[0xF4] = "After Throw (Mounting)", [0xF5] = "Throw (Mounting)",
	},
	[0x03] = { -- Samus
		[0xDD] = "Appearing",
		[0xDE] = "Starting Charge Shot", [0xDF] = "Charging", [0xE0] = "Shooting",
		[0xE1] = "Starting Charge Shot (Aerial)", [0xE2] = "Shooting (Aerial)",
		[0xE3] = "Screw Attack", [0xE4] = "Screw Attack (Aerial)",
		[0xE5] = "Bomb", [0xE6] = "Bomb (Aerial)",
	},
	[0x04] = { -- Luigi
		[0xDC] = "Jab 3",
		[0xDE] = "Appearing",
		[0xDF] = "Fireball", [0xE0] = "Fireball (Aerial)",
		[0xE1] = "Up-Special", [0xE2] = "Up-Special (Aerial)",
		[0xE3] = "Down-Special", [0xE4] = "Down-Special (Aerial)",
	},
	[0x05] = { -- Link
		[0xDC] = "Jab 3", [0xDD] = "Jab Loop (Start)", [0xDE] = "Jab Loop", [0xDF] = "Jab Loop (End)",
		[0xE0] = "Appearing", [0xE1] = "Appearing",
		[0xE2] = "Up-Special", [0xE3] = "Up-Special (End)", [0xE4] = "Up-Special (Aerial)",
		[0xE5] = "Boomerang", [0xE6] = "Catching Boomerang", [0xE7] = "Missing Boomerang",
		[0xE8] = "Boomerang (Aerial)", [0xE9] = "Catching Boomerang (Aerial)", [0xEA] = "Missing Boomerang (Aerial)",
		[0xEB] = "Bomb", [0xEC] = "Bomb (Aerial)",
	},
	[0x06] = { -- Yoshi
		[0xDD] = "Appearing",
		[0xDE] = "Up-Special", [0xDF] = "Up-Special (Aerial)",
		[0xE0] = "Start Down-Special", [0xE1] = "Landing while Down-Special",
		[0xE2] = "Start Down-Special(Aerial)", [0xE3] = "Falling while Down-Special",
		[0xE4] = "N-Special", [0xE5] = "Succeeding N-Special", [0xE6] = "N-Special (End)",
		[0xE7] = "N-Special (Aerial)", [0xE8] = "Succeeding N-Special (Aerial)", [0xE9] = "N-Special (Aerial) (End)",
	},
	[0x07] = { -- Captain Falcon
		[0xDC] = "Jab 3", [0xDD] = "Jab Loop (Start)", [0xDE] = "Jab Loop", [0xDF] = "Jab Loop (End)",
		[0xE0] = "Appearing", [0xE1] = "Appearing (Aerial)", [0xE2] = "Blue Falcon", [0xE3] = "Blue Falcon",
		[0xE4] = "Falcon Punch", [0xE5] = "Falcon Punch (Aerial)",
		[0xE6] = "Down-Special", [0xE7] = "Velocity X Down-Special (Aerial)",
		[0xE8] = "Landing while Down-Special", [0xE9] = "Down-Special (Aerial)", [0xEA] = "Bumping while Down-Special",
		[0xEB] = "Falcon Dive", [0xEC] = "Cathing Enemy while F Dive", [0xED] = "Falcon Dive (End)",
		[0xEE] = "Falcon Dive (Aerial)",
	},
	[0x08] = { -- Kirby
		[0xFA] = "Staring", [0xFB] = "Staring",
		[0xDC] = "Jab Loop (Start)", [0xDD] = "Jab Loop", [0xDE] = "Jab Loop (End)",
		[0xDF] = "Jumping (Aerial) [4]", [0xE0] = "Jumping (Aerial) [3]",
		[0xE1] = "Jumping (Aerial) [2]", [0xE2] = "Jumping (Aerial) [1]", [0xE3] = "Jumping (Aerial) [0]",
		-- Mario
		[0xE7] = "Fireball", [0xE8] = "Fireball (Aerial)",
		-- Luigi
		[0xE9] = "Fireball", [0xEA] = "Fireball (Aerial)",
		-- Fox
		[0xEB] = "Laser", [0xEC] = "Laser (Aerial)",
		-- Samus
		[0xED] = "Charge Shot (Start)", [0xEE] = "Charging", [0xEF] = "Shooting",
		[0xF0] = "Charge Shot (Aerial) (Start)", [0xF1] = "Shooting (Aerial)",
		-- DK
		[0xF2] = "Charge (Start)", [0xF3] = "Charge (Aerial) (Start)",
		[0xF4] = "Charging", [0xF5] = "Charging (Aerial)",
		[0xF6] = "Punching", [0xF7] = "Punching (Aerial)",
		[0xF8] = "Maximum Punching", [0xF9] = "Maximum Punching (Aerial)",
		-- Pikachu
		[0xFC] = "Lightning", [0xFD] = "Lightning (Aerial)",
		-- Ness
		[0xFE] = "PK Fire", [0xFF] = "PK Fire (Aerial)",

		[0x100] = "Up-Special", [0x101] = "Landing while Up-Special",
		[0x102] = "Up-Special (Aerial)", [0x103] = "Falling while Up-Special",
		[0x104] = "Down-Special (Start)", [0x106] = "Down-Special", [0x107] = "Canceling Down-Special",
		[0x108] = "Down-Special (Aerial) (Start)", [0x109] = "Falling while Down-Special (Aerial)",
		[0x10A] = "Landing while Down-Special", [0x10B] = "Falling while Down-Special", [0x10C] = "Cancelling Down-Special (Aerial)",
		[0x10D] = "N-Special (Start)", [0x10E] = "N-Special", [0x10F] = "N-Special (End)",
		[0x110] = "Inhaling while N-Special (Start)", [0x111] = "Inhaling while N-Special",
		[0x112] = "Spitting while N-Special",
		[0x113] = "Stuffing while N-Special", [0x114] = "Switching Direction while Stuffing while N-Special",
		[0x115] = "Copying",
		[0x116] = "N-Special (Aerial) (Start)", [0x117] = "N-Special (Aerial)", [0x118] = "N-Special (Aerial) (End)",
		[0x119] = "Inhaling while N-Special (Aerial) (Start)", [0x11A] = "Inhaling while N-Special (Aerial)",
		[0x11C] = "Spitting while N-Special", [0x11D] = "Stuffing while N-Special (Aerial)", [0x11E] = "Copying (Aerial)",

		-- Link
		[0x11F] = "Boomerang", [0x120] = "Catching Boomerang", [0x121] = "Missing Boomerang",
		[0x122] = "Boomerang (Aerial)", [0x123] = "Catching Boomerang (Aerial)", [0x124] = "Missing Boomerang (Aerial)",
		-- Jigglypuff
		[0x125] = "Pound", [0x126] = "Pound (Aerial)",
		-- Captain Falcon
		[0x127] = "Falcon Punch", [0x128] = "Falcon Punch (Aerial)",
		-- Yoshi
		[0x129] = "N-Special", [0x12A] = "Succeeding N-Special", [0x12B] = "N-Special (End)",
		[0x12C] = "N-Special (Aerial)", [0x12D] = "Succeeding N-Special (Aerial)", [0x12E] = "N-Special (Aerial) (End)",
	},
	[0x09] = { -- Pikachu
		[0xDD] = "Appearing",
		[0xDE] = "N-Special", [0xDF] = "N-Special (Aerial)",
		[0xE0] = "Down-Special (Start)", [0xE1] = "Down-Special", [0xE2] = "Getting Thundered", [0xE3] = "Down-Special (End)",
		[0xE4] = "Down-Special (Aerial) (Start)", [0xE5] = "Down-Special (Aerial)", [0xE6] = "Getting Thundered (Aerial)", [0xE7] = "Down-Special (Aerial) (End)",
		[0xE8] = "Up-Special (Start)", [0xE9] = "Up-Special", [0xEA] = "Up-Special (End)",
		[0xEB] = "Up-Special (Aerial) (Start)", [0xEC] = "Up-Special (Aerial)", [0xED] = "Up-Special (Aerial) (End)",
	},
	[0x0A] = { -- Jigglypuff
		[0xDF] = "Jumping (Aerial) [4]", [0xE0] = "Jumping (Aerial) [3]",
		[0xE1] = "Jumping (Aerial) [2]", [0xE2] = "Jumping (Aerial) [1]", [0xE3] = "Jumping (Aerial) [0]",
		[0xE4] = "Appearing", [0xE5] = "Appearing",
		[0xE6] = "Pound", [0xE7] = "Pound (Aerial)",
		[0xE8] = "Sing", [0xE9] = "Sing (Aerial)",
		[0xEA] = "Rest", [0xEB] = "Rest (Aerial)",
	},
	[0x0B] = { -- Ness
		[0xDC] = "Jab 3",
		[0xDE] = "Appearing", [0xDF] = "Appearing", [0xE1] = "Appearing",
		[0xE2] = "PK Fire", [0xE3] = "PK Fire (Aerial)",
		[0xE4] = "PK Thunder (Start)", [0xE5] = "PK Thunder", [0xE6] = "PK Thunder (End)", [0xE7] = "PKTA",
		[0xE8] = "PK Thunder (Aerial) (Start)", [0xE9] = "PK Thunder (Aerial)", [0xEA] = "PK Thunder (Aerial) (End)",
		[0xEB] = "Clashing during PKTA", [0xEC] = "PKTA (Aerial)",
		[0xED] = "Down-Special (Start)", [0xEE] = "Down-Special", [0xEF] = "Cureing", [0xF0] = "Down-Special (End)",
		[0xF1] = "Down-Special (Aerial) (Start)", [0xF2] = "Down-Special (Aerial)", [0xF3] = "Cureing (Aerial)", [0xF4] = "Down-Special (Aerial) (End)",
	},
	[0x0C] = { -- Master Hand
		[0xDD] = "Idle", [0xDE] = "Selecting Move",
		[0xDF] = "Slapping",
		[0xE0] = "Shooing",
		[0xE1] = "Launching", [0xE2] = "Flying", [0xE3] = "Landing",
		[0xE4] = "Walking (Start)", [0xE5] = "Walking", [0xE7] = "Flicking",
		[0xE8] = "Charging (Start)", [0xE9] = "Charging", [0xEA] = "Landing", [0xEB] = "Punching",
		[0xEC] = "Pointing (Start)", [0xED] = "Poking", [0xEE] = "Pointing",
		[0xEF] = "Drilling",
		[0xF0] = "Punching",
		[0xF1] = "Pulling Gun", [0xF2] = "Shooting Gun", [0xF3] = "Aiming Gun",
		[0xF4] = "Punching (Start)", [0xF5] = "Punching", [0xF6] = "Punching (End)",
		[0xF7] = "Slamming", [0xF8] = "Slamming (Start)",
		[0xF9] = "Dying (Start)", [0xFA] = "Dying",
		[0xFC] = "Appearing",
	},
	[0x0D] = { -- Metal Mario
		[0xDC] = "Jab 3",
		[0xDE] = "Appearing",
		[0xDF] = "Fireball", [0xE0] = "Fireball (Aerial)",
		[0xE1] = "Up-Special", [0xE2] = "Up-Special (Aerial)",
		[0xE3] = "Down-Special", [0xE4] = "Down-Special (Aerial)",
	},
	[0x1A] = { -- Giant DK
		[0xDD] = "Appearing",
		[0xDE] = "Charge (Start)", [0xDF] = "Charge (Aerial) (Start)",
		[0xE0] = "Charging", [0xE1] = "Charging (Aerial)",
		[0xE2] = "Punching", [0xE3] = "Punching (Aerial)",
		[0xE4] = "Maximum Punching", [0xE5] = "Maximum Punching (Aerial)",
		[0xE6] = "Up-Special", [0xE7] = "Up-Special (Aerial)",
		[0xE8] = "Down-Special (Start)", [0xE9] = "Down-Special", [0xEA] = "Down-Special (End)",
		[0xEB] = "Standing (Mounting)",
		[0xEC] = "Walking slowly (Mounting)", [0xED] = "Walking (Mounting)", [0xEE] = "Walking quickly (Mounting)",
		[0xEF] = "Switching direction (Mounting)",
		[0xF0] = "Jump (Mounting) (Start)", [0xF1] = "Jumping (Mounting)", [0xF2] = "Landing (Mounting)",
		[0xF4] = "After Throw (Mounting)", [0xF5] = "Throw (Mounting)",
	},
};
};