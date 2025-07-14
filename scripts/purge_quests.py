from notion_client import Client
import os

print("🔷 Initiating quest purge...")

# Read env vars directly — works in GitHub Actions if secrets are passed
NOTION_API_KEY = os.getenv("NOTION_API_KEY", "").strip()
QUEST_DB_ID = os.getenv("QUEST_DB_ID", "").strip()
CHECKBOX_PROPERTY = "Checkbox"

if not NOTION_API_KEY:
    raise RuntimeError("❌ NOTION_API_KEY is missing.")
if not QUEST_DB_ID:
    raise RuntimeError("❌ QUEST_DB_ID is missing.")

notion = Client(auth=NOTION_API_KEY)

def fetch_quests_to_reset():
    print(f"📄 Querying database {QUEST_DB_ID} for checked quests…")
    try:
        response = notion.databases.query(
            database_id=QUEST_DB_ID,
            filter={
                "property": CHECKBOX_PROPERTY,
                "checkbox": {"equals": True}
            }
        )
        results = response.get("results", [])
        print(f"✅ Found {len(results)} quests to reset.")
        return [page["id"] for page in results]
    except Exception as e:
        print(f"❌ Error fetching quests: {e}")
        return []

def reset_checkbox(page_id):
    try:
        notion.pages.update(
            page_id=page_id,
            properties={CHECKBOX_PROPERTY: {"checkbox": False}}
        )
        print(f"✅ Reset checkbox for page: {page_id}")
    except Exception as e:
        print(f"❌ Failed to reset {page_id}: {e}")

def main():
    quests = fetch_quests_to_reset()
    if not quests:
        print("🎉 No quests to purge. All clean.")
        return
    print("⚔️ Purging quests...")
    for q in quests:
        reset_checkbox(q)
    print("🎯 Purge complete.")

if __name__ == "__main__":
    main()
