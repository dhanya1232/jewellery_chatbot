from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.ai_service import JewelleryAIService

load_dotenv()

app = FastAPI(title="Multimodal Jewellery Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = JewelleryAIService.from_env()


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    reply: str


class ImageToTextResponse(BaseModel):
    description: str


class TextToImageRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=2000)
    size: str = Field(default="1024x1024")


class TextToImageResponse(BaseModel):
    image_base64: str
    note: str | None = None


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    try:
        return ChatResponse(reply=service.chat_text(req.message))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chat error: {exc}") from exc


@app.post("/api/image-to-text", response_model=ImageToTextResponse)
async def image_to_text(image: UploadFile = File(...)) -> ImageToTextResponse:
    try:
        content = await image.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty image upload")
        description = service.image_to_text(content, filename=image.filename or "uploaded_image")
        return ImageToTextResponse(description=description)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Image-to-text error: {exc}") from exc


@app.post("/api/text-to-image", response_model=TextToImageResponse)
def text_to_image(req: TextToImageRequest) -> TextToImageResponse:
    try:
        b64 = service.text_to_image(req.prompt, size=req.size)
        if not b64:
            return TextToImageResponse(
                image_base64="",
                note="Fallback mode: add HUGGINGFACE_API_TOKEN to generate images.",
            )
        return TextToImageResponse(image_base64=b64)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Text-to-image error: {exc}") from exc


frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")




@app.get("/styles.css")
def styles() -> FileResponse:
    return FileResponse(frontend_dir / "styles.css")


@app.get("/app.js")
def app_js() -> FileResponse:
    return FileResponse(frontend_dir / "app.js")

@app.get("/")
def root() -> FileResponse:
    return FileResponse(frontend_dir / "index.html")
