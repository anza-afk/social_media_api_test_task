from pydantic import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    EMAILHUNTER_API_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()
