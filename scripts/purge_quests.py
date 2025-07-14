from notion_client import Client
import os

if not os.getenv("CI"):
    from dotenv import load_dotenv
    load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY", "").strip()
QUEST_DB_ID = os.getenv("QUEST_DB_ID", "").strip()
CHECKBOX_PROPERTY = "Checkbox"

if not NOTION_API_KEY or not QUEST_DB_ID:
    raise RuntimeError("❌ Missing NOTION_API_KEY or QUEST_DB_ID")

notion = Client(auth=NOTION_API_KEY)

def fetch_quests_to_reset():
    print(f"🔷 Querying DB: {QUEST_DB_ID}")
    try:
        response = notion.databases.query(
            database_id=QUEST_DB_ID,
            filter={
                "property": CHECKBOX_PROPERTY,
                "checkbox": {"equals": True}
            }
        )
        results = response.get("results", [])
        print(f"🔷 Found {len(results)} pages to reset.")
        for r in results:
            print(f" - Page ID: {r['id']}")
        return [r["id"] for r in results]
    except Exception as e:
        print(f"❌ Error fetching quests: {e}")
        return []

def reset_checkbox(page_id):
    try:
        notion.pages.update(
            page_id=page_id,
            properties={CHECKBOX_PROPERTY: {"checkbox": False}}
        )
        print(f"✅ Reset page: {page_id}")
    except Exception as e:
        print(f"❌ Failed to reset {page_id}: {e}")

if __name__ == "__main__":
    print("🔷 Initiating quest purge...")
    quests = fetch_quests_to_reset()

    if not quests:
        print("✅ No quests to purge. All clean.")
    else:
        for q in quests:
            reset_checkbox(q)
        print("🎯 Purge complete.")
