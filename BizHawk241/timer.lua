require "os";

local count = 0
local goal = 20000
local start_time = nil
local end_time = nil
while true do
    if start_time == nil and count > 1 then
        print("started taking time")
        start_time = os.time()
    end
    count = count + 1
    if count > goal then
        end_time = os.time()
        break
    end

    -- Do the next frame (and pray things don't break)
    emu.frameadvance();
end

local elapsed = end_time - start_time
print(elapsed)