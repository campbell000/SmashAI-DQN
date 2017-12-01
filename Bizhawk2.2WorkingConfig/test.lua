-- We SHOULD be able to load this file in Bizhawk and have it simply work. If everything goes according to plan, and you
-- have the server.py file running, you should see "Hello World" in the output. In the server, you should see the message
-- "Hi from Bizhawk!"

http = require("socket.http")
local ltn12 = require 'ltn12'
local request_body = [[login=user&password=123]]

print("Making request to local server at 8081...")
-- Make a request
res = {}
xx, xxx, xxxx, xxxxx = http.request {
    method = "POST",
    url = "http://127.0.0.1:8081",
    headers =
    {
        ["Content-Type"] = "application/x-www-form-urlencoded";
        ["Content-Length"] = #request_body;
    },
    source = ltn12.source.string(request_body),
    sink = ltn12.sink.table(res)
}
print(xx)
print(xxx)
print(xxxx)
print(xxxxx)

print("Done, now reading response...")
response =  table.concat(res)
print(response)

print("Finished")