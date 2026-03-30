from fastapi import FastAPI #imports the FastAPI class from the fastapi module, which is used to create a FastAPI application instance.
from fastapi.middleware.cors import CORSMiddleware  # allows html communicate with python    
from pydantic import BaseModel
import bambulabs_api as bl
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


printer = None # mantains the printer connection
class ConnectRequest(BaseModel):
    ip: str 
    access_code: str
    serial: str

class CommandRequest(BaseModel):
    command: str

@app.post("/connect")                                                  
def connect(request: ConnectRequest):
    global printer
    try:
        printer = bl.Printer(request.ip, request.access_code, request.serial) #creates the printer object with your credentials
        printer.connect()
        time.sleep(2)  # Wait for the connection to establish   
        return {"ok":True, "message": f"Connected to {request.ip} successfully!"}
    except Exception as e:                                                        
        return {"ok":False, "message": f"Failed to connect to {request.ip}!"}
    
@app.get("/status")
def status():
    global printer
    if printer is None:
        return {"ok": False, "message": "Not connected to any printer."}
    try:
        return {
            "ok": True,
            "status": printer.get_status(),
            "nozzle_temp": printer.get_nozzle_temperature(),
            "bed_temp": printer.get_bed_temperature(),
            "print_progress": printer.get_print_progress(),
            "remaining_time": printer.get_remaining_time(),
            "layer": printer.get_current_layer(),
            "total_layers": printer.get_total_layer(),
            "filename": printer.get_gcode_filename(), 
        }
    except Exception as e:
        return {"ok": False, "message": "Failed to retrieve printer status."}

@app.post("/command")
def command(req: CommandRequest):
    global printer
    if printer is None:
        return {"ok": False, "message": "Not connected to any printer."}
    try:
        if req.command == "pause":
            printer.pause_print()
        elif req.command == "resume":
            printer.resume_print()
        elif req.command == "cancel":
            printer.cancel_print()
        else:
            return {"ok": False, "message": "Invalid command."}
        return {"ok": True, "message": f"Command '{req.command}' executed successfully!"}
    except Exception as e:
        return {"ok": False, "message": f"Failed to execute command '{req.command}'."}

@app.get("/ams")
def ams():
    global printer
    if printer is None:
        return {"ok": False, "message": "Not connected to any printer."}
    try:
        ams_info = printer.get_ams_info()
        slots = []
        if ams_info:
            for tray in ams_info.get("trays", []):
                for slot in tray.get("slots", []):
                    slots.append({
                        "slot_id": slot.get("slot_id"),
                        "status": slot.get("status"),
                        "material": slot.get("material"),
                        "color": "#" + slot.get("color", "000000"),  # Default to black if no color provided
                        "remain" : slot.get("remain", 0),
                        "active" : slot.get("id") == ams_info.get("tray_now"),
                    })
        return {"ok": True, "ams_slots": slots}
    except Exception as e:
        return {"ok": False, "message": "Failed to retrieve AMS information."}

if __name__ == "__main__": 
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

