import os
import math
import uuid
import hashlib
from datetime import datetime
from fastapi import FastAPI, Request, BackgroundTasks
import httpx
from dotenv import load_dotenv
from supabase import create_client, Client

from core.security import encrypt_sensitive_data, compute_photo_checksum
from core.immudb_client import vault
from services.turnout_model import turnout_engine

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="Blood Donation Intelligence Node")

# Initialize Supabase 
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    print("WARNING: Supabase credentials missing. Database operations will fail.")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

@app.get("/")
async def health_check():
    """Basic pulse check to ensure the backend is alive."""
    return {"status": "operational", "system": "Intelligent Mobilisation Platform"}

@app.get("/api/v1/campaigns")
async def get_campaigns():
    """Mocks the active blood drives for the frontend dashboard."""
    return [
        {
            "id": "11111111-1111-1111-1111-111111111111", 
            "name": "Red Cross Central Emergency Camp", 
            "location": "Jamtha, Maharashtra",
            "lat": 18.5204,
            "lon": 73.8567
        }
    ]

@app.get("/api/v1/audit")
async def get_audit_logs(limit: int = 50):
    """Mocks the immudb ledger for the transparency UI."""
    return [
        {
            "id": "log-1",
            "event_type": "SYSTEM_START",
            "timestamp": datetime.utcnow().isoformat(),
            "hash": "a1b2c3d4e5f6..."
        }
    ]

@app.post("/webhook/telegram")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Handles Telegram interactions, specifically the Absolute Consent Circuit Breaker.
    """
    update = await request.json()
    
    # Check if this is a button click (Callback Query)
    if "callback_query" in update:
        callback = update["callback_query"]
        user_id = str(callback["from"]["id"])
        action = callback["data"]
        message_id = callback["message"]["message_id"]
        chat_id = callback["message"]["chat"]["id"]

        if action == "opt_out":
            # 1. Supabase Revocation: Cut off outbound queues
            if supabase:
                supabase.table("donors").update({"opt_in_current_drive": False}).eq("telegram_chat_id", user_id).execute()
            
            # 2. immudb Revocation: Write immutable audit log
            revocation_time = datetime.utcnow().isoformat()
            vault.secure_store_donor(
                donor_uuid=user_id, 
                encrypted_id="[REVOKED]", 
                photo_hash="[REVOKED]", 
                consent_timestamp=f"REVOKED_AT:{revocation_time}"
            )

            # 3. Notify User via Telegram Bot API
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": "Consent revoked. You have been removed from all mobilization queues. Your revocation timestamp has been securely logged."
            }
            async with httpx.AsyncClient() as client:
                await client.post(url, json=payload)

    return {"status": "ok"}

def calculate_haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates distance in km between two coordinate points."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi, dlambda = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0)**2
    return round(R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))), 2)

@app.post("/api/register")
async def register_donor(request: Request):
    payload = await request.json()
    donor_uuid = str(uuid.uuid4())
    
    # 1. IMMUDB: Sensitive Audit Payload
    raw_national_id = payload.get("national_id", "0000000000")
    encrypted_id = encrypt_sensitive_data(raw_national_id)
    photo_sha256 = compute_photo_checksum(b"fake_image_data_from_upload")
    
    ledger_success = vault.secure_store_donor(
        donor_uuid=donor_uuid,
        encrypted_id=encrypted_id,
        photo_hash=photo_sha256,
        consent_timestamp=datetime.utcnow().isoformat()
    )

    # 2. SUPABASE: Operational Attributes
    # Hash the phone number so the operational database doesn't hold plain-text PII
    phone_hash = hashlib.sha256(payload.get("phone").encode()).hexdigest()
    
    # Calculate distance to the dummy camp we just created in Baner, Pune
    camp_lat, camp_lon = 18.5590, 73.7768
    donor_lat, donor_lon = payload.get("lat"), payload.get("lon")
    distance_km = calculate_haversine(camp_lat, camp_lon, donor_lat, donor_lon)
    
    # Run the ML prediction based on the architecture specs
    turnout_prob = turnout_engine.calculate_probability(
        distance_km=distance_km, 
        age=payload.get("age", 22), 
        past_donations=0, 
        engagement_rate=1.0
    )

    supabase_data = {
        "id": donor_uuid,
        "camp_id": "11111111-1111-1111-1111-111111111111", 
        "phone_hash": phone_hash,
        "preferred_language": payload.get("language", "en"),
        "slot_time": "2026-10-15T10:00:00Z", 
        "photo_storage_path": "/mock/path/photo.jpg",
        "age": payload.get("age", 22), 
        "donor_location": f"POINT({donor_lon} {donor_lat})",
        "turnout_probability": turnout_prob
    }
    
    supabase_success = False
    if supabase:
        try:
            supabase.table("donors").insert(supabase_data).execute()
            supabase_success = True
        except Exception as e:
            print(f"Supabase Insert Error: {e}")

    return {
        "status": "Intake & Separation Complete",
        "distance_to_camp_km": distance_km,
        "ledger_commit_status": "Success" if ledger_success else "Failed",
        "supabase_commit_status": "Success" if supabase_success else "Failed"
    }