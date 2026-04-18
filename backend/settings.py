from functools import lru_cache
from typing import Any, Dict

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3-flash-preview"
    debug: bool = False

    mongo_uri: str = "http://localhost:27017"
    mongo_db_name: str = "itr_filing"

    csfle_master_key: str = ""
    csfle_key_vault_namespace: str = "encryption.__keyVault"

    seed_first_name: str = ""
    seed_middle_name: str = ""
    seed_last_name: str = ""
    seed_pan_number: str = ""
    seed_aadhar_number: str = ""
    seed_aadhar_pincode: str = ""
    seed_mobile_number: str = ""
    seed_email: str = ""
    seed_password: str = ""

    def get_seed_user_dict(self) -> Dict[str, Any]:
        """Returns the seed user details as a dictionary formatted for document storage."""
        return {
            "first_name": self.seed_first_name,
            "middle_name": self.seed_middle_name,
            "last_name": self.seed_last_name,
            "pan_number": self.seed_pan_number,
            "aadhar_number": self.seed_aadhar_number,
            "aadhar_pincode": self.seed_aadhar_pincode,
            "mobile_number": self.seed_mobile_number,
            "email": self.seed_email,
            "password": self.seed_password
        }


@lru_cache()
def get_settings():
    return Settings()
