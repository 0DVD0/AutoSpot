from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "AutoSpot API"
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    supabase_url: str
    supabase_service_role_key: str
    supabase_post_images_bucket: str = "App-Img"
    supabase_avatar_image_bucket: str = "Usr-Avtr"
    ai_service_url: str = "http://127.0.0.1:8001"
    ai_service_timeout: float = 180.0
settings = Settings()