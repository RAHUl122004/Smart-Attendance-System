import os
import streamlit as st
from supabase import create_client, Client

url = None
key = None

try:
    if "SUPABASE_URL" in st.secrets:
        url = st.secrets["SUPABASE_URL"]
    if "SUPABASE_KEY" in st.secrets:
        key = st.secrets["SUPABASE_KEY"]
except Exception:
    pass

if not url:
    url = os.environ.get("SUPABASE_URL")
if not key:
    key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    search_paths = [
        os.path.join(os.path.dirname(__file__), "..", ".env"),
        os.path.join(os.path.dirname(__file__), "..", "..", ".env"),
        os.path.join(os.path.dirname(__file__), "..", "..", ".streamlit", "secrets.toml"),
    ]
    for env_path in search_paths:
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if "=" in line and not line.startswith("#"):
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k == "SUPABASE_URL" and not url:
                            url = v
                        elif k == "SUPABASE_KEY" and not key:
                            key = v

supabase: Client = create_client(url, key)