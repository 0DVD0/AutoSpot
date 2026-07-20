from pydantic import BaseModel, EmailStr, Field

class LoginData(BaseModel):
    password: str = Field(min_length=6, max_length=20)
    email: EmailStr

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str