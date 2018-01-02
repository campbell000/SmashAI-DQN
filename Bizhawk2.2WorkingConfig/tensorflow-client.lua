-- This module contains methods for sending data to the tensorflow server, and retrieving predictions based on the data

http = require("socket.http")
require "list"
local ltn12 = require 'ltn12'
local CLIENT = {}

-- NOTE: These must match the ACTION_MAP variable in server.py. The indices must line up correctly
local TRAIN = 0
local EVAL = 1
local HELLO = 2

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

function CLIENT.convert_map_to_form_data(buffer_size, stateList, action)
    local data = ""
    local keyvals = {}
    local i = 1

    -- For each state, convert the key/values into form elements
    for state_num = 1, buffer_size do
        local state = List.popleft(stateList)
        for k, v in pairs(state) do
            local key = "s"..state_num.."_"..k
            keyvals[i] =  key.."="..v
            i = (i + 1)
        end
        List.pushright(stateList, state)
    end

    -- Format the form elements into something resembling a POST body
    for i = 1, #keyvals do
        data = data..keyvals[i].."&"
    end

    -- Add the action
    data = data.."action="..action
    return data
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
function CLIENT.send_data_for_training(buffer_size, data)
    local request_body = CLIENT.convert_map_to_form_data(buffer_size, data, TRAIN)
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



