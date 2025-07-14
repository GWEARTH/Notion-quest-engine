from notion_client import Client
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY", "").strip()
DATABASE_ID = os.getenv("QUEST_DB_ID", "").strip()

if not NOTION_API_KEY:
    raise ValueError("❌ NOTION_API_KEY is missing. Check your .env or secrets.")
if not DATABASE_ID:
    raise ValueError("❌ QUEST_DB_ID is missing. Check your .env or secrets.")

notion = Client(auth=NOTION_API_KEY)

print(f"🔷 Testing connection to database: {DATABASE_ID}")

try:
    db = notion.databases.retrieve(database_id=DATABASE_ID)
    title = "(No Title)"
    if db.get("title"):
        title_parts = []
        for part in db["title"]:
            if part["type"] == "text":
                title_parts.append(part["plain_text"])
        title = "".join(title_parts) or "(No Title)"
    print(f"✅ SUCCESS: Connected to database '{title}' ({DATABASE_ID})")
except Exception as e:
    print(f"❌ ERROR: Could not access database.\nReason: {e}")
