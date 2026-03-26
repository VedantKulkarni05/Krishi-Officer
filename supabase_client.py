import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = (
    os.getenv("SUPABASE_KEY")
    or os.getenv("SUPABASE_ANON_KEY")
    or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
)

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "Missing Supabase configuration. Set SUPABASE_URL and SUPABASE_KEY "
        "(or SUPABASE_ANON_KEY / NEXT_PUBLIC_* equivalents) in .env."
    )

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)