"""
Routes package initialization.

This module exports all route modules for easy importing in main.py.
"""
from app.routes import auth, tasks

__all__ = ["auth", "tasks"]