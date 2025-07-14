import os
from notion_client import Client
from dotenv import load_dotenv

# Load .env if running locally
load_dotenv()

DATABASE_ID = os.getenv("QUEST_DB_ID")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")

if not DATABASE_ID or not NOTION_API_KEY:
    raise ValueError("❌ Missing QUEST_DB_ID or NOTION_API_KEY in environment.")

notion = Client(auth=NOTION_API_KEY)

CHECKBOX_PROPERTY = "Completed"  # adjust if your property name is different


def fetch_quests_to_purge():
    pages = []
    start_cursor = None

    while True:
        response = notion.databases.query(
            database_id=DATABASE_ID,
            filter={
                "property": CHECKBOX_PROPERTY,
                "checkbox": {
                    "equals": True
                }
            },
            start_cursor=start_cursor
        )
        pages.extend(response["results"])

        if response.get("has_more"):
            start_cursor = response["next_cursor"]
        else:
            break

    return pages


def uncheck_quest(page_id):
    notion.pages.update(
        page_id=page_id,
        properties={
            CHECKBOX_PROPERTY: {
                "checkbox": False
            }
        }
    )


if __name__ == "__main__":
    print("🔷 Initiating quest purge...")

    try:
        quests = fetch_quests_to_purge()
    except Exception as e:
        print(f"❌ Error while querying database: {e}")
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
