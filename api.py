from fastapi import FastAPI
from pydantic import BaseModel
from simplifier import EmailSimplifier

app = FastAPI()
simplifier = EmailSimplifier("config.yaml")

class SimplifyRequest(BaseModel):
    text: str

class SimplifyResponse(BaseModel):
    simplified_text: str

@app.post("/simplify-text", response_model=SimplifyResponse)
def simplify(req: SimplifyRequest):
    return SimplifyResponse(simplified_text=simplifier.simplify_text(req.text))
