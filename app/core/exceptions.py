"""
Custom exceptions for the application.
"""
from fastapi import HTTPException


class APIException(HTTPException):
    """Base exception for API errors."""

    def __init__(self, status_code: int = 500, detail: str = "Internal server error"):
        """Initialize the exception."""
        super().__init__(status_code=status_code, detail=detail) 