import os
import requests

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("QUEST_DB_ID")

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

query_url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
update_url = "https://api.notion.com/v1/pages/"

def fetch_pages_marked_for_purge():
    """
    Fetch all pages where the 'Checkbox' property is True.
    These are the quests to be purged.
    """
    pages = []
    has_more = True
    next_cursor = None

    while has_more:
        payload = {
            "filter": {
                "property": "Checkbox",
                "checkbox": {"equals": True}
            }
        }

        if next_cursor:
            payload["start_cursor"] = next_cursor

        response = requests.post(query_url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        pages.extend(data["results"])
        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor")

    return pages

def purge_quest(page_id):
    """
    Set the 'Checkbox' property of a page to False — purge it.
    """
    payload = {
        "properties": {
            "Checkbox": {
                "checkbox": False
            }
        }
    }

    response = requests.patch(f"{update_url}{page_id}", headers=headers, json=payload)
    response.raise_for_status()
    print(f"Purged quest: {page_id}")

if __name__ == "__main__":
    print("🔷 Initiating quest purge...")
    quests_to_purge = fetch_pages_marked_for_purge()

    if not quests_to_purge:
        print("✅ No quests marked for purge. All is clean.")
    else:
        print(f"⚔️ Found {len(quests_to_purge)} quests to purge.")
        for quest in quests_to_purge:
            purge_quest(quest["id"])
        print("🎯 Purge complete.")
