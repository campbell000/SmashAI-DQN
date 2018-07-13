-- This module contains methods for sending data to the tensorflow server, and retrieving predictions based on the data

http = require("socket.http")
require "list"
local ltn12 = require 'ltn12'
local CLIENT = {}

-- NOTE: These must match the ACTION_MAP variable in server.py. The indices must line up correctly
local TRAIN = 0
local EVAL = 1
local HELLO = 2


function CLIENT.convert_map_to_form_data(buffer_size, currentStateList, clientID, action)
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

    -- Add the client ID. Maybe
    buffer[#buffer+1] = "clientID="..clientID

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

-- This function sends data to the server with the intention of training the model. It returns an action to perform as output
function CLIENT.send_data_for_training(buffer_size, currentState, clientID)
    local request_body = CLIENT.convert_map_to_form_data(buffer_size, currentState, clientID, TRAIN)
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



