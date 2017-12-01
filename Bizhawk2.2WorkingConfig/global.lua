require ".gameConstants";

function isRDRAM(value)
		return type(value) == "number" and value >= 0 and value < N64.RDRAMSize;
	end

-- Checks whether a value is a pointer in to N64 RDRAM on the system bus
function isPointer(value)
	return type(value) == "number" and value >= N64.RDRAMBase and value < N64.RDRAMBase + N64.RDRAMSize;
end

function dereferencePointer(address)
		if type(address) == "number" and address >= 0 and address < (N64.RDRAMSize - 4) then
			address = mainmemory.read_u32_be(address);
			if isPointer(address) then
				return address - N64.RDRAMBase;
			end
		end
end

function keyExists(array, key)
    return array[key] ~= nil
end