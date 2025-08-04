from typing import Generator
from app.config.database import get_supabase_client

def get_supabase_client_dependency():
    """Get Supabase client dependency"""
    return get_supabase_client() 