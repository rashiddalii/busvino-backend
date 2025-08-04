from supabase import create_client, Client
from app.config.settings import settings

def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

# Global Supabase client instance
supabase_client = get_supabase_client() 