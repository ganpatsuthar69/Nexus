"""API Dependencies.

Provides database session generator and API key authentication.
"""

import os
from typing import Generator

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from app.db.session import SessionLocal

# API Key security scheme (expects X-API-Key header)
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Get the expected secret from the environment
API_AUTH_SECRET = os.getenv("API_AUTH_SECRET", "change-me")


def get_db() -> Generator[Session, None, None]:
    """Yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_api_key(
    api_key_header: str | None = Security(api_key_header),
    api_key: str | None = None,
) -> str:
    """Verifies the API key against the environment secret.
    
    Accepts the key either via the X-API-Key header or an api_key query parameter (used for SSE).
    Returns the actor ("API User") on success, raises 401 on failure.
    """
    key_to_verify = api_key_header or api_key
    
    if not key_to_verify:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key",
        )
    
    if key_to_verify != API_AUTH_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    
    return "API User"
