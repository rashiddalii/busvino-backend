from supabase import create_client, Client
from app.config.settings import settings

def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

# Remove global client initialization to avoid Vercel compatibility issues
# supabase_client = get_supabase_client() 