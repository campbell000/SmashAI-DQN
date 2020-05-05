---
--- Created by ascam.
--- DateTime: 12/11/2017 9:24 PM
---
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

function tablelength(T)
    local count = 0
    for _ in pairs(T) do count = count + 1 end
    return count
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

function generateRandomString(length)
    local res = ""
    for i = 1, length do
        res = res .. string.char(math.random(97, 122))
    end
    return res
end


-- see if the file exists
function file_exists(file)
    local f = io.open(file, "rb")
    if f then f:close() end
    return f ~= nil
end

-- get all lines from a file, returns an empty
-- list/table if the file does not exist
function lines_from(file)
    if not file_exists(file) then return {} end
    lines = {}
    for line in io.lines(file) do
        lines[#lines + 1] = line
    end
    return lines
end

function get_num_frames_per_state(game_name)
    -- tests the functions above
    local file = '../shared_constants.properties'
    local lines = lines_from(file)

    for k,v in pairs(lines) do
        a, b = string.match(v, "(.*)%.(.*)")
        if a == game_name then
            c, d = string.match(v, "(.*)=(.*)")
            return tonumber(d)
        end
    end
    error("Couldn't find number of frames per state for game: "..game_name)
end

