from typing import Generator
from app.config.database import supabase_client

def get_supabase_client():
    """Get Supabase client dependency"""
    return supabase_client 