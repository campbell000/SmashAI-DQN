-- You SHOULD be able to load this file in Bizhawk and double click on it to run it. If everything goes according to plan,
--and you have tensorflow-server.py file running, you should see POST data in the python console
comm.getluafunctionslist()
comm.httpTest()
comm.httpSetPostUrl("http://127.0.0.1:8081")
comm.httpPostScreenshot()