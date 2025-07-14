import os
import requests
from dotenv import load_dotenv

# Load .env if running locally
load_dotenv()

DATABASE_ID = os.getenv("QUEST_DB_ID")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")

if not DATABASE_ID or not NOTION_API_KEY:
    raise ValueError("❌ Missing QUEST_DB_ID or NOTION_API_KEY in environment.")

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

CHECKBOX_PROPERTY = "Completed"  # Change this if your checkbox property has a different name


def fetch_quests_to_purge():
    """
    Query the database for pages where the checkbox is True.
    """
    query_url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    payload = {
        "filter": {
            "property": CHECKBOX_PROPERTY,
            "checkbox": {
                "equals": True
            }
        }
    }

    resp = requests.post(query_url, headers=HEADERS, json=payload)
    if resp.status_code == 404:
        raise ValueError("❌ Database not found. Check that DATABASE_ID is correct and shared with the integration.")
    if resp.status_code == 401:
        raise ValueError("❌ Unauthorized. Check that NOTION_API_KEY is correct.")
    resp.raise_for_status()

    data = resp.json()
    pages = data.get("results", [])
    return pages


def uncheck_quest(page_id):
    """
    Set the checkbox to False for a given page.
    """
    update_url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {
        "properties": {
            CHECKBOX_PROPERTY: {
                "checkbox": False
            }
        }
    }

    resp = requests.patch(update_url, headers=HEADERS, json=payload)
    resp.raise_for_status()


if __name__ == "__main__":
    print("🔷 Initiating quest purge...")

    try:
        quests = fetch_quests_to_purge()
    except Exception as e:
        print(e)
        exit(1)

    if not quests:
        print("✅ No quests marked for purge. All is clean.")
    else:
        print(f"⚔️ Found {len(quests)} quests to purge.")
        for quest in quests:
            page_id = quest["id"]
            try:
                uncheck_quest(page_id)
                print(f" - ✅ Unchecked quest: {page_id}")
            except Exception as e:
                print(f" - ❌ Failed to uncheck {page_id}: {e}")

        print("🎯 Purge complete.")
