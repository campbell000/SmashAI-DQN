-- This module contains methods for sending data to the tensorflow server, and retrieving predictions based on the data

http = require("socket.http")
local ltn12 = require 'ltn12'
local CLIENT = {}

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

function CLIENT.convert_map_to_form_data(map)
    local data = ""
    local keyvals = {}
    local i = 1
    for k, v in pairs(map) do
        keyvals[i] =  k.."="..v
        i = (i + 1)
    end

    for i = 1, #keyvals do
        if i == #keyvals then
            data = data..keyvals[i]
        else
            data = data..keyvals[i].."&"
        end
    end
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
function CLIENT.send_data_for_training(data)
    data["action"] = "train"
    local request_body = CLIENT.convert_map_to_form_data(data)
    return CLIENT.send_request_to_tensorflow_server(request_body)
end

-- This function sends data to the server and does NOT traing the model. It simply returns a prediction.
function CLIENT.send_data_for_prediction(data)
    data["action"] = "eval"
    local request_body = CLIENT.convert_map_to_form_data(data)
    return CLIENT.send_request_to_tensorflow_server(request_body)
end

function CLIENT.say_hello(data)
    data["action"] = "hello"
    local request_body = CLIENT.convert_map_to_form_data(data)
    return CLIENT.send_request_to_tensorflow_server(request_body)
end

function CLIENT.fake_say_hello(data)
    data["action"] = "hello"
    local request_body = CLIENT.convert_map_to_form_data(data)
    print(request_body)
end

return CLIENT



