import base64
import os
from dataclasses import dataclass
from typing import Optional

import httpx


@dataclass
class AIConfig:
    huggingface_token: Optional[str]
    chat_model: str = "HuggingFaceH4/zephyr-7b-beta"
    vision_model: str = "Salesforce/blip-image-captioning-large"
    image_model: str = "stabilityai/stable-diffusion-2-1"


class JewelleryAIService:
    def __init__(self, config: AIConfig):
        self.config = config
        self.base_url = "https://api-inference.huggingface.co/models"

    @classmethod
    def from_env(cls) -> "JewelleryAIService":
        return cls(
            AIConfig(
                huggingface_token=os.getenv("HUGGINGFACE_API_TOKEN"),
                chat_model=os.getenv("HF_CHAT_MODEL", "HuggingFaceH4/zephyr-7b-beta"),
                vision_model=os.getenv("HF_VISION_MODEL", "Salesforce/blip-image-captioning-large"),
                image_model=os.getenv("HF_IMAGE_MODEL", "stabilityai/stable-diffusion-2-1"),
            )
        )

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.config.huggingface_token:
            headers["Authorization"] = f"Bearer {self.config.huggingface_token}"
        return headers

    def chat_text(self, message: str) -> str:
        if not self.config.huggingface_token:
            return (
                "[Fallback] Add HUGGINGFACE_API_TOKEN for live AI responses. "
                f"Jewellery tip: For daily wear, choose 14k gold or platinum settings. You asked: '{message}'."
            )

        prompt = (
            "You are a jewellery expert assistant. Be concise and practical.\n"
            f"Customer: {message}\nAssistant:"
        )
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 220, "temperature": 0.7, "return_full_text": False},
        }
        response = httpx.post(
            f"{self.base_url}/{self.config.chat_model}",
            headers=self._headers(),
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list) and data and "generated_text" in data[0]:
            return data[0]["generated_text"].strip()
        return "I couldn't generate a response right now. Please try again."

    def image_to_text(self, image_bytes: bytes, filename: str = "image.png") -> str:
        if not self.config.huggingface_token:
            return (
                "[Fallback] Add HUGGINGFACE_API_TOKEN for live image analysis. "
                "This appears to be a jewellery item; I can normally identify style, metal tone, and gemstone clues."
            )

        headers = self._headers()
        headers.pop("Content-Type", None)
        response = httpx.post(
            f"{self.base_url}/{self.config.vision_model}",
            headers=headers,
            content=image_bytes,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list) and data and "generated_text" in data[0]:
            return data[0]["generated_text"].strip()
        return "I couldn't analyze the image right now. Please retry."

    def text_to_image(self, prompt: str, size: str = "1024x1024") -> str:
        if not self.config.huggingface_token:
            return ""

        width, height = 1024, 1024
        try:
            width, height = [int(x) for x in size.lower().split("x")]
        except Exception:
            pass

        payload = {
            "inputs": f"High quality product photography of jewellery: {prompt}",
            "parameters": {"width": width, "height": height},
        }
        response = httpx.post(
            f"{self.base_url}/{self.config.image_model}",
            headers=self._headers(),
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        return base64.b64encode(response.content).decode("utf-8")
