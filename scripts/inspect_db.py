import os, requests

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("QUEST_DB_ID")

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

def inspect_database():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()

    print(f"\n📋 Database: {data.get('title', [{}])[0].get('plain_text', '')}")
    print("Properties:")
    for name, prop in data["properties"].items():
        print(f" - {name} ({prop['type']})")

if __name__ == "__main__":
    inspect_database()
