-- You SHOULD be able to load this file in Bizhawk and double click on it to run it. If everything goes according to plan,
--and you have tensorflow-server.py file running, you should see POST data in the python console

client = require("tensorflow-client")
data = {}
data["attr1"] = "Hi from bizhawk!"

local resp = client.say_hello(data)
print("Response from tensorflow server: "..resp)