http = require("socket.http")
local ltn12 = require 'ltn12'

local function convert_map_to_form_data(map)
    data = ""
    keyvals = {}
    for k, v in pairs(map) do
        keyvals.insert(k.."="..v)
    end

    for i = 1, #keyvals do
        if i == 1 then
            data = keyvals[i]
        elseif i == #keyvals then
            data = data..keyvals[i]
        else
            data = data..keyvals[i].."&"
        end
    end
    return data
end

local function send_request_to_tensorflow_server(request_body)
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


function send_data_for_training(data) end



