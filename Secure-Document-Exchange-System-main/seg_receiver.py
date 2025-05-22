from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from xml_utils import verify_signature
import ssl
import uvicorn


from fastapi.middleware.cors import CORSMiddleware




app = FastAPI()



# Templates for simple UI
templates = Jinja2Templates(directory="templates")

# In-memory store for last received XML & status
last_received = {
    "xml": None,
    "status": None,
    "error": None
}

@app.post("/receive")
async def receive_document(request: Request):
    try:
        data = await request.json()
        xml = data['xml']
        signature = bytes.fromhex(data['signature'])

        if not verify_signature(xml, signature, 'certs/sender.crt'):
            last_received.update({"xml": xml, "status": "Signature verification failed.", "error": True})
            return JSONResponse(content={"error": "Signature verification failed."}, status_code=400)

        last_received.update({"xml": xml, "status": "Signature verified successfully.", "error": False})
        print("✅ Signature Verified.")
        print("📄 Received XML:\n", xml)
        return {"status": "Success"}

    except Exception as e:
        last_received.update({"xml": None, "status": str(e), "error": True})
        print("❌ Error:", str(e))
        return JSONResponse(content={"error": str(e)}, status_code=400)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "xml": last_received["xml"], "status": last_received["status"], "error": last_received["error"]})

if __name__ == "__main__":
    uvicorn.run("seg_receiver:app",
                host="0.0.0.0",
                port=5001,
                ssl_certfile="certs/receiver.crt",
                ssl_keyfile="certs/receiver.key",
                ssl_ca_certs="certs/rootCA.pem",
                ssl_cert_reqs=ssl.CERT_REQUIRED)
