from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from app.utils.ai_helper import generate_service_description

router = APIRouter(prefix="/api", tags=["ai"])


class GenerateRequest(BaseModel):
    service_name: str
    keywords: Optional[str] = ""


@router.post("/generate-text")
def generate_text(body: GenerateRequest):
    try:
        text = generate_service_description(body.service_name, body.keywords or "")
        return {"text": text}
    except ValueError as exc:
        return JSONResponse({"error": str(exc)}, status_code=400)
    except Exception as exc:
        return JSONResponse({"error": f"AI error: {exc}"}, status_code=500)
