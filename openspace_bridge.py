# Copyright 2026 Michael Fowler
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0

import asyncio
import websockets
import json
import csv

# Lua script templates for OpenSpace state injection
LUA_MOVE_SAT = "openspace.setPropertyValueSingle('Scene.SurrogateSat.Translation.Position', {{{x}, {y}, {z}}});"
LUA_SET_COLOR = "openspace.setPropertyValueSingle('Scene.SurrogateSat.Renderable.Color', {{{r}, {g}, {b}}});"

async def stream_to_openspace():
    # OpenSpace WebSocket API endpoint
    uri = "ws://localhost:4680/all_nodes" 
    
    try:
        async with websockets.connect(uri) as websocket:
            print("--- Sentinel Node: Connected to OpenSpace ---")
            
            with open("flight_telemetry.csv", "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Extract kinematic data from telemetry log
                    x = float(row["True_X"])
                    y = float(row["True_Y"])
                    z = float(row["True_Z"])
                    is_jammed = row["Jamming_Active"] == "True"

                    # 1. Update Position
                    # Convert coordinates from km to meters for OpenSpace rendering engine
                    pos_script = LUA_MOVE_SAT.format(x=x*1000, y=y*1000, z=z*1000)
                    
                    # 2. Update Render State
                    if is_jammed:
                        # Alert state (Red) indicates active EW jamming
                        color_script = LUA_SET_COLOR.format(r=1, g=0, b=0)
                    else:
                        # Nominal state (Blue/White)
                        color_script = LUA_SET_COLOR.format(r=0, g=0.5, b=1)

                    # Package Lua scripts into OpenSpace JSON payload (Topic 4: Lua Scripts)
                    payload = {
                        "topic": 4, 
                        "type": "luascript",
                        "payload": {"script": pos_script + color_script}
                    }

                    await websocket.send(json.dumps(payload))
                    
                    print(f"Streaming T+{row['Time_sec']}s | Jammed: {is_jammed}")
                    
                    # Throttle transmission stream to ~20 Hz
                    await asyncio.sleep(0.05) 

    except Exception as e:
        print(f"Connection Failed: {e}. Verify OpenSpace instance is running and WebSocket API is enabled.")

if __name__ == "__main__":
    asyncio.run(stream_to_openspace())