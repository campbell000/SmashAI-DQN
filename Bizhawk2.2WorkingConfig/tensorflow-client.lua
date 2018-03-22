-- This module contains methods for sending data to the tensorflow server, and retrieving predictions based on the data

http = require("socket.http")
require "list"
local ltn12 = require 'ltn12'
local CLIENT = {}

-- NOTE: These must match the ACTION_MAP variable in server.py. The indices must line up correctly
local TRAIN = 0
local EVAL = 1
local HELLO = 2

function dump(node)
    -- to make output beautiful
    local function tab(amt)
        local str = ""
        for i=1,amt do
            str = str .. "\t"
        end
        return str
    end

    local cache, stack, output = {},{},{}
    local depth = 1
    local output_str = "{\n"

    while true do
        local size = 0
        for k,v in pairs(node) do
            size = size + 1
        end

        local cur_index = 1
        for k,v in pairs(node) do
            if (cache[node] == nil) or (cur_index >= cache[node]) then

                if (string.find(output_str,"}",output_str:len())) then
                    output_str = output_str .. ",\n"
                elseif not (string.find(output_str,"\n",output_str:len())) then
                    output_str = output_str .. "\n"
                end

                -- This is necessary for working with HUGE tables otherwise we run out of memory using concat on huge strings
                table.insert(output,output_str)
                output_str = ""

                local key
                if (type(k) == "number" or type(k) == "boolean") then
                    key = "["..tostring(k).."]"
                else
                    key = "['"..tostring(k).."']"
                end

                if (type(v) == "number" or type(v) == "boolean") then
                    output_str = output_str .. tab(depth) .. key .. " = "..tostring(v)
                elseif (type(v) == "table") then
                    output_str = output_str .. tab(depth) .. key .. " = {\n"
                    table.insert(stack,node)
                    table.insert(stack,v)
                    cache[node] = cur_index+1
                    break
                else
                    output_str = output_str .. tab(depth) .. key .. " = '"..tostring(v).."'"
                end

                if (cur_index == size) then
                    output_str = output_str .. "\n" .. tab(depth-1) .. "}"
                else
                    output_str = output_str .. ","
                end
            else
                -- close the table
                if (cur_index == size) then
                    output_str = output_str .. "\n" .. tab(depth-1) .. "}"
                end
            end

            cur_index = cur_index + 1
        end

        if (size == 0) then
            output_str = output_str .. "\n" .. tab(depth-1) .. "}"
        end

        if (#stack > 0) then
            node = stack[#stack]
            stack[#stack] = nil
            depth = cache[node] == nil and depth + 1 or depth - 1
        else
            break
        end
    end

    -- This is necessary for working with HUGE tables otherwise we run out of memory using concat on huge strings
    table.insert(output,output_str)
    output_str = table.concat(output)

    print(output_str)
end

function CLIENT.convert_map_to_form_data(buffer_size, currentStateList, previousStateList, action)
    local currkeyvals = {}
    local prevkeyvals = {}
    local i = 1
    local j = 1

    -- For each state, convert the key/values into form elements
    for state_num = 1, buffer_size do
        local state = List.popleft(currentStateList) -- Get state, which contains data for both players
        for playerID, playerData in pairs(state) do -- for players 1 and 2....
            for dataKey, dataValue in pairs(playerData) do
                local key = "c["..(state_num - 1).."]".."["..playerID.."]["..dataKey.."]"
                currkeyvals[i] =  key.."="..dataValue
                i = (i + 1)
            end
        end
        List.pushright(currentStateList, state)
    end

    for state_num = 1, buffer_size do
        local state = List.popleft(previousStateList) -- Get state, which contains data for both players
        for playerID, playerData in pairs(state) do -- for players 1 and 2....
            for dataKey, dataValue in pairs(playerData) do
                local key = "p["..(state_num - 1).."]".."["..playerID.."]["..dataKey.."]"
                prevkeyvals[j] =  key.."="..dataValue
                j = (j + 1)
            end
        end
        List.pushright(previousStateList, state)
    end

    -- Format the form elements into something resembling a POST body
    local buffer = {}
    for i = 1, #currkeyvals do
        buffer[#buffer+1] = currkeyvals[i].."&"
    end

    for j = 1, #prevkeyvals do
        buffer[#buffer+1] = prevkeyvals[j].."&"
    end

    -- Add the action
    buffer[#buffer+1] = "action="..action
    return table.concat(buffer)
end

function CLIENT.send_request_to_tensorflow_server(request_body)
    -- send request as a POST
    res = {}
    local a, b, c, d = http.request {
        method = "POST",
        url = "http://127.0.0.1:8081",
        headers =
        {
            ["Content-Length"] = #request_body;
        },
        source = ltn12.source.string(request_body),
        sink = ltn12.sink.table(res)
    }

    response =  table.concat(res)
    return response
end

-- This function sends data to the server with the intention of training the model. It returns an output
function CLIENT.send_data_for_training(buffer_size, currentState, prevState)
    local request_body = CLIENT.convert_map_to_form_data(buffer_size, currentState, prevState, TRAIN)
    return CLIENT.send_request_to_tensorflow_server(request_body)
end

-- This function sends data to the server and does NOT traing the model. It simply returns a prediction.
function CLIENT.send_data_for_prediction(data)
    data["action"] = EVAL
    local request_body = CLIENT.convert_map_to_form_data(data)
    return CLIENT.send_request_to_tensorflow_server(request_body)
end

function CLIENT.say_hello()
    local helloData = "action="..HELLO
    return CLIENT.send_request_to_tensorflow_server(helloData)
end

function CLIENT.fake_say_hello(data)
    data["action"] = HELLO
    local request_body = CLIENT.convert_map_to_form_data(data)
    print(request_body)
end

return CLIENT



