import warnings
from io import BytesIO
import httpx
from ollama import ChatResponse, Client, ResponseError
from PIL import Image, ImageOps
from pydantic import ValidationError
from app.vlm_schema import VlmPrediction


class VlmPredictor:
    def __init__(self, model_name:str = "gemma3:4b", host: str = "http://127.0.0.1:11434"):

        self.model_name = model_name
        self.client = Client(host=host, timeout= 120.0)

    def close(self):
        self.client.close()


    def _prepare_image(self, image: Image.Image) -> bytes:
        if not isinstance(image, Image.Image):
            raise TypeError("Image must be PIL Image")

        prepared = ImageOps.exif_transpose(image).convert("RGB")
        prepared.thumbnail((1024, 1024), Image.Resampling.LANCZOS)

        with BytesIO() as buffer:
            prepared.save(buffer, format="JPEG", quality=95)
            return buffer.getvalue()

    def _parse_response(self, response: ChatResponse) -> VlmPrediction:
        if not response.done or response.done_reason != "stop":
            raise RuntimeError("VLM response was not completed")

        content = (response.message.content or "").strip()

        if not content:
            raise RuntimeError("Ollama returned no content")

        try:
            prediction = VlmPrediction.model_validate_json(content)
        except ValidationError as error:
            raise RuntimeError("VLM returned a invalid prediction") from error

        if prediction.brand is None and prediction.model is not None:
            raise RuntimeError("VLM returned a model with no brand")

        return prediction

    def predict_image(self, image: Image.Image) -> VlmPrediction:
        image_bytes = self._prepare_image(image)

        prompt = ("Identify the exact make and model of the "
                    "main vehicle in this image. "
                    "Use the European-market vehicle name. "
                    "Return only JSON with the keys brand and model. "
                    "Use null for any field that cannot be "
                    "identified reliably. "
                    "If brand is null, model must also be null. "
                    "Do not include the year, generation, variant, "
                    "explanations, or confidence scores. "
                    "Do not invent missing details.")

        try: 
            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                        "images": [image_bytes]
                    }
                ],
                format=VlmPrediction.model_json_schema(),
                stream=False,
                options={
                    "num_ctx": 8192,
                    "num_predict": 256,
                    "temperature": 0,
                    "seed": 42
                }
            )
        except httpx.TimeoutException as error:
            raise RuntimeError("Ollama took too long to responde") from error
        except ResponseError as error:
            raise RuntimeError(f"Ollama error: {error.error}") from error
        except httpx.HTTPError as error:
            raise RuntimeError("HTTP communication with Ollama failed") from error

        return self._parse_response(response)