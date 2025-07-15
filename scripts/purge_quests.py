import os
from notion_client import Client

# Read secrets from environment (set by GitHub Actions)
NOTION_API_KEY = os.getenv("NOTION_API_KEY", "").strip()
QUEST_DB_ID = os.getenv("QUEST_DB_ID", "").strip()
CHECKBOX_PROPERTY = "Checkbox"

if not NOTION_API_KEY:
    raise RuntimeError("❌ NOTION_API_KEY is missing.")
if not QUEST_DB_ID:
    raise RuntimeError("❌ QUEST_DB_ID is missing.")

notion = Client(auth=NOTION_API_KEY)


def fetch_quests_to_reset():
    """
    Fetch all pages where Checkbox == True.
    """
    pages_to_reset = []
    try:
        print(f"📄 Querying database {QUEST_DB_ID} for checked quests…")
        response = notion.databases.query(
            database_id=QUEST_DB_ID,
            filter={
                "property": CHECKBOX_PROPERTY,
                "checkbox": {"equals": True}
            }
        )
        for page in response.get("results", []):
            pages_to_reset.append(page["id"])
    except Exception as e:
        print(f"❌ Error fetching quests: {e}")
    return pages_to_reset


def reset_checkbox(page_id):
    """
    Set Checkbox = False for given page.
    """
    try:
        notion.pages.update(
            page_id=page_id,
            properties={
                CHECKBOX_PROPERTY: {"checkbox": False}
            }
        )
        print(f"✅ Reset quest: {page_id}")
    except Exception as e:
        print(f"❌ Failed to reset {page_id}: {e}")


def main():
    print("🔷 Initiating quest purge…")

    quests = fetch_quests_to_reset()

    if not quests:
        print("🎉 No quests to purge. All clean.")
        return

    print(f"⚔️ Found {len(quests)} quests to reset.")
    for q in quests:
        reset_checkbox(q)

    print("🏁 Purge complete!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"🔥 Script crashed: {e}")
        raise
