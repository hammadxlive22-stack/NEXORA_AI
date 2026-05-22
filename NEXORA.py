from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = FastAPI(title="NEXORA AI - Master Core")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hardcoded details (Directly from you)
SENDER_EMAIL = "hammadlive22@gmail.com"
SENDER_PASSWORD = "qaov rkrl pexm gsew"

VALID_API_KEYS = {"NEXORA-MASTER-KEY": "♾️"}
PENDING_OTPS = {}

class ChatRequest(BaseModel):
    messages: List[dict]

class OTPRequest(BaseModel):
    email: str

class VerifyRequest(BaseModel):
    email: str
    otp: str

def send_mail(to_email: str, code: str):
    try:
        msg = MIMEMultipart()
        msg['Subject'] = "🔒 NEXORA Verification"
        msg.attach(MIMEText(f"Your code: {code}", 'plain'))
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()
        return True
    except:
        return False

@app.post("/api/auth/send-otp")
async def send_otp(req: OTPRequest):
    code = str(secrets.randbelow(900000) + 100000)
    PENDING_OTPS[req.email.strip().lower()] = code
    if send_mail(req.email.strip().lower(), code):
        return {"status": "success"}
    raise HTTPException(status_code=500, detail="Mail failed")

@app.post("/api/auth/verify-otp")
async def verify(req: VerifyRequest):
    if PENDING_OTPS.get(req.email.strip().lower()) == req.otp:
        key = f"NEXORA-{secrets.token_hex(6).upper()}"
        VALID_API_KEYS[key] = "♾️"
        return {"status": "success", "nexora_api_key": key}
    raise HTTPException(status_code=400, detail="Invalid OTP")

@app.post("/v1/chat/completions")
async def chat(req: ChatRequest, auth: str = Header(None)):
    if not auth or auth.split(" ")[1] not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"choices": [{"message": {"content": "⚙️ System Online. NEXORA engine functional."}}]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
