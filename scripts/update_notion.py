import os
from pathlib import Path
from notion_client import Client
from dotenv import load_dotenv

# Load .env from repo root explicitly
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Grab secrets from env
notion_token = os.environ.get("NOTION_TOKEN")
database_id = os.environ.get("DATABASE_ID")

# Safety check
if not notion_token or not database_id:
    raise ValueError("❌ NOTION_TOKEN or DATABASE_ID not found in environment variables!")

# Initialize Notion client
notion = Client(auth=notion_token)

def main():
    print("🚀 Adding a page to your Notion database...")

    # Add a page to the DB
    notion.pages.create(
        parent={"database_id": database_id},
        properties={
            "Name": {"title": [{"text": {"content": "✅ Quest from Codespaces"}}]}
        }
    )

    print("🎉 Success! Page created in Notion.")

if __name__ == "__main__":
    main()
