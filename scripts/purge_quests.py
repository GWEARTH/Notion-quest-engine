from notion_client import Client
import os

# 🔷 Only load .env locally (optional)
if not os.getenv("CI"):  # In GitHub Actions, CI=true
    from dotenv import load_dotenv
    load_dotenv()

# 🔷 Environment variables
NOTION_API_KEY = os.getenv("NOTION_API_KEY", "").strip()
QUEST_DB_ID = os.getenv("QUEST_DB_ID", "").strip()
CHECKBOX_PROPERTY = "Checkbox"  # Change if your property name is different

if not NOTION_API_KEY:
    raise ValueError("❌ NOTION_API_KEY is missing.")
if not QUEST_DB_ID:
    raise ValueError("❌ QUEST_DB_ID is missing.")

notion = Client(auth=NOTION_API_KEY)


def fetch_quests_to_reset():
    """
    Fetch all pages in the database where Checkbox == True.
    """
    pages_to_reset = []
    try:
        response = notion.databases.query(
            database_id=QUEST_DB_ID,
            filter={
                "property": CHECKBOX_PROPERTY,
                "checkbox": {"equals": True}
            }
        )
        for page in response.get("results", []):
            pages_to_reset.append(page["id"])
        return pages_to_reset

    except Exception as e:
        print(f"❌ Error fetching quests: {e}")
        return []


def reset_checkbox(page_id):
    """
    Set Checkbox property to False on the given page.
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
    print("🔷 Initiating quest purge...")

    quests = fetch_quests_to_reset()

    if not quests:
        print("✅ No quests to purge. All clean.")
        return

    print(f"⚔️ Found {len(quests)} quests to reset.")
    for q in quests:
        reset_checkbox(q)

    print("🎯 Purge complete.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"🔥 Script crashed: {e}")
        raise
