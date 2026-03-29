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
    acess_code: str
    serial: str

@app.post("/connect")                                                  
def connect(request: ConnectRequest):
    global printer
    try:
        printer = bl.BambulabsPrinter(request.ip, request.acess_code, request.serial) #creates the printer object with your credentials
        printer.connect()
        time.sleep(2)  # Wait for the connection to establish   
        return {"ok":True, "message": f"Connected to {request.ip} successfully!"}
    except Exception as e:                                                        
        return {"ok":False, "message": f"Failed to connect to {request.ip}!"}
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)