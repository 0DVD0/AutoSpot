from pydantic import BaseModel, ConfigDict, Field

class VlmPrediction(BaseModel):
   model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)

   brand: str | None = Field(min_length=1, max_length=100)
   model: str | None = Field(min_length=1, max_length=100)
        