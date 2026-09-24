from datetime import datetime
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel

from app.services.ai_service import categorize_complaint
from app.services.nlp_service import detect_language, translate_to_english


router = APIRouter()


class ComplaintCreate(BaseModel):
    citizen_name: str
    citizen_phone: str
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    description: str
    language: Optional[str] = "auto"
    category: Optional[str] = None


class ComplaintResponse(BaseModel):
    complaint_id: str
    status: str
    category: str
    department: str
    priority: str
    created_at: str


fake_complaints_db = []


@router.post("/", response_model=ComplaintResponse, status_code=201)
async def create_complaint(complaint: ComplaintCreate):
    detected_lang = complaint.language
    if detected_lang == "auto":
        detected_lang = detect_language(complaint.description)

    english_text = translate_to_english(complaint.description, detected_lang)

    ai_result = await categorize_complaint(english_text)

    complaint_id = f"LS-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    record = {
        "complaint_id": complaint_id,
        "citizen_name": complaint.citizen_name,
        "citizen_phone": complaint.citizen_phone,
        "location": complaint.location,
        "latitude": complaint.latitude,
        "longitude": complaint.longitude,
        "original_text": complaint.description,
        "english_text": english_text,
        "language": detected_lang,
        "category": ai_result.get("category", "General"),
        "department": ai_result.get("department", "Municipal"),
        "priority": ai_result.get("priority", "Medium"),
        "status": "Pending",
        "created_at": datetime.now().isoformat()
    }
    fake_complaints_db.append(record)

    return ComplaintResponse(
        complaint_id=complaint_id,
        status="Pending",
        category=record["category"],
        department=record["department"],
        priority=record["priority"],
        created_at=record["created_at"]
    )


@router.post("/voice", response_model=ComplaintResponse, status_code=201)
async def create_voice_complaint(
    citizen_name: str = Form(...),
    citizen_phone: str = Form(...),
    location: str = Form(...),
    audio: UploadFile = File(...)
):
    from app.services.nlp_service import transcribe_audio

    audio_bytes = await audio.read()
    transcribed_text = await transcribe_audio(audio_bytes)

    complaint = ComplaintCreate(
        citizen_name=citizen_name,
        citizen_phone=citizen_phone,
        location=location,
        description=transcribed_text,
        language="auto"
    )
    return await create_complaint(complaint)


@router.get("/")
async def list_complaints(status: Optional[str] = None, category: Optional[str] = None):
    results = fake_complaints_db
    if status:
        results = [c for c in results if c["status"] == status]
    if category:
        results = [c for c in results if c["category"] == category]
    return {"total": len(results), "complaints": results}


@router.get("/{complaint_id}")
async def get_complaint(complaint_id: str):
    for c in fake_complaints_db:
        if c["complaint_id"] == complaint_id:
            return c
    raise HTTPException(status_code=404, detail="Complaint not found")


@router.patch("/{complaint_id}/status")
async def update_status(complaint_id: str, new_status: str):
    for c in fake_complaints_db:
        if c["complaint_id"] == complaint_id:
            c["status"] = new_status
            return {"message": "Status updated", "complaint_id": complaint_id, "status": new_status}
    raise HTTPException(status_code=404, detail="Complaint not found")