from dataclasses import asdict

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from msg_convert import OutlookMsgSimplifier
from simplifier import EmailSimplifier

app = FastAPI()
simplifier = EmailSimplifier("config.yaml")
msg_simplifier = OutlookMsgSimplifier("config.yaml")


class SimplifyRequest(BaseModel):
    text: str


class SimplifyResponse(BaseModel):
    simplified_text: str


@app.post("/simplify-text", response_model=SimplifyResponse)
def simplify(req: SimplifyRequest):
    return SimplifyResponse(simplified_text=simplifier.simplify_text(req.text))


@app.post("/simplify-msg")
async def simplify_msg(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".msg"):
        raise HTTPException(status_code=400, detail="Please upload a valid .msg file")

    try:
        content = await file.read()
        message = msg_simplifier.simplify_msg_bytes(content)
        return asdict(message)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive API guardrail
        raise HTTPException(status_code=500, detail=f"Unable to process .msg file: {exc}") from exc
