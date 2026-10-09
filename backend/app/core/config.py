"""
Centralized configuration via pydantic-settings.

Reads from environment variables / .env file and validates at startup
so we fail fast if a required key is missing.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # ── App ───────────────────────────────────────────
    APP_ENV: str = "development"
    DEBUG: bool = True

    # ── Database ──────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://repoinsight:repoinsight@db:5432/repoinsight"
    DATABASE_URL_SYNC: str = "postgresql://repoinsight:repoinsight@db:5432/repoinsight"

    # ── Redis ─────────────────────────────────────────
    REDIS_URL: str = "redis://redis:6379/0"

    # ── Auth ──────────────────────────────────────────
    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24 hours

    # ── Symmetric encryption for sensitive tokens at rest ──
    # Used by app.core.crypto. Generate with: openssl rand -base64 32
    # In production, the startup check refuses to boot without it.
    ENCRYPTION_KEY: str = ""
    # Comma-separated list of older keys, accepted for decryption only.
    # Lets you rotate the primary key without invalidating existing tokens.
    ENCRYPTION_KEY_ROTATION: str = ""

    # ── GitHub ────────────────────────────────────────
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    # Webhook secret for AI PR Reviewer. If set, incoming webhooks must
    # include a matching X-Hub-Signature-256 HMAC. Leave blank in dev.
    GITHUB_WEBHOOK_SECRET: str = ""

    # ── Slack integration ──
    # Get these from api.slack.com after creating an app for RepoInsight.
    # All optional in dev — feature simply becomes unavailable if unset.
    SLACK_CLIENT_ID: str = ""
    SLACK_CLIENT_SECRET: str = ""
    SLACK_SIGNING_SECRET: str = ""

    # Backend URL is used to construct the OAuth redirect URI for Slack.
    # Default suits local dev; production deploys should override via env.
    BACKEND_URL: str = "http://localhost:8000"

    # ── AI provider order ────────────────────────────────
    # Providers are tried left to right; a failure (rate limit, outage)
    # falls through to the next one. Only providers with a key are used.
    AI_PROVIDER_ORDER: str = "gemini,groq,claude,openai"

    # ── Google Gemini (free tier — https://aistudio.google.com/apikey) ──
    GEMINI_API_KEY: str = ""
    # Quality model (docs, onboarding, chat) and fast model (audits, JSON).
    GEMINI_MODEL: str = "gemini-3.6-flash"
    GEMINI_FAST_MODEL: str = "gemini-3.5-flash-lite"
    # Keeps Gemini's built-in "thinking" short so responses stay fast.
    # Set to empty to use the model's default.
    GEMINI_REASONING_EFFORT: str = "low"

    # ── Groq (free tier — https://console.groq.com/keys) ──
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_FAST_MODEL: str = "llama-3.3-70b-versatile"

    # ── OpenAI (optional, paid) ───────────────────────────
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # ── Anthropic Claude (optional, paid API credits) ─────
    ANTHROPIC_API_KEY: str = ""
    # Default model — used for prose-heavy features (docs, onboarding guide).
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"
    # Fast model — used for short structured outputs (audit, security scan,
    # task generation, architecture diagram). Roughly 3-5x faster than Sonnet
    # on the kind of token volumes those features produce.
    ANTHROPIC_HAIKU_MODEL: str = "claude-haiku-4-5-20251001"

    # ── Chroma ────────────────────────────────────────
    CHROMA_HOST: str = "chroma"
    CHROMA_PORT: int = 8000

    # ── URLs ──────────────────────────────────────────
    FRONTEND_URL: str = "http://localhost:3000"

    # ── Rate Limiting ─────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 60
    # Comma-separated list of IP addresses or CIDR blocks for the reverse
    # proxy / load balancer in front of this service. Only requests coming
    # from these addresses are allowed to set X-Forwarded-For. Empty list
    # (the default) means no XFF is trusted — correct for local dev and
    # for any deployment without a known proxy.
    # Examples:
    #   "127.0.0.1"         — nginx on same host
    #   "10.0.0.0/8"        — anything in private VPC
    #   "127.0.0.1,10.0.0.0/8"
    TRUSTED_PROXIES: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
