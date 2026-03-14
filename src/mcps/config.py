from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Server
    host: str = "127.0.0.1"
    port: int = 8000

    # OAuth
    auth_users: str = ""  # "user1:$2b$...,user2:$2b$..."
    auth_secret_key: str = "dev-secret-change-me"
    auth_issuer: str = "http://localhost:8000"

    # Jackett
    jackett_url: str = "http://localhost:9117"
    jackett_api_key: str = ""

    # TMDB
    tmdb_api_key: str = ""

    # Transmission
    transmission_host: str = "localhost"
    transmission_port: int = 9091
    transmission_path: str = "/transmission/rpc"
    transmission_user: str | None = None
    transmission_pass: str | None = None
    transmission_ssl: bool = False

    def get_users(self) -> dict[str, str]:
        """Parse AUTH_USERS into {username: bcrypt_hash} dict."""
        if not self.auth_users:
            return {}
        users = {}
        for entry in self.auth_users.split(","):
            entry = entry.strip()
            if ":" not in entry:
                continue
            username, hash_ = entry.split(":", 1)
            users[username.strip()] = hash_.strip()
        return users


settings = Settings()
