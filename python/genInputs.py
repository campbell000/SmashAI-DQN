JOYSTICK = {
    "CENTER": "{[\"X Axis\"] = 0, [\"Y Axis\"] = 0}",
    "UP": "{[\"X Axis\"] = 0, [\"Y Axis\"] = 127}",
    "LEFT_UP": "{[\"X Axis\"] = -127, [\"Y Axis\"] = 127}",
    "LEFT": "{[\"X Axis\"] = -127, [\"Y Axis\"] = 0}",
    "LEFT_DOWN": "{[\"X Axis\"] = -127, [\"Y Axis\"] = -127}",
    "DOWN": "{[\"X Axis\"] = 0, [\"Y Axis\"] = -127}",
    "RIGHT_DOWN": "{[\"X Axis\"] = 127, [\"Y Axis\"] = -127}",
    "RIGHT": "{[\"X Axis\"] = 127, [\"Y Axis\"] = 0}",
    "RIGHT_UP": "{[\"X Axis\"] = 127, [\"Y Axis\"] = 127}",
}

BUTTONS = {
    "ATTACK": "{[\"A\"] = \"True\" }",
    "SPECIAL": "{[\"B\"] = \"True\" }",
    "JUMP": "{[\"C Right\"] = \"True\" }",
    "SHEILD": "{[\"Z\"] = \"True\" }",
    "GRAB": "{[\"R\"] = \"True\" }",
    "NOTHING": "{}"
}

for b in BUTTONS:
    for j in JOYSTICK:
        print("INPUTS."+str(j)+"_"+str(b)+" = {"+BUTTONS[b]+", "+JOYSTICK[j]+"}")