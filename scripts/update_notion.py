import os
import datetime
from notion_client import Client
print("⚡ Starting Notion update script")

# Load environment variables
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
SCORE_DB_ID = os.getenv("SCORE_DB_ID")
MAIN_DB_ID = os.getenv("MAIN_DB_ID")

# Initialize Notion client
notion = Client(auth=NOTION_API_KEY)

# Constants
TARGET_PAGE_NAME = "Null"
LOG_FILE = "logs/output.log"

def log(message):
    timestamp = datetime.datetime.utcnow().strftime("[%Y-%m-%d %H:%M:%S UTC]")
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} {message}\n")
    print(message)

def get_page_by_name(db_id, name):
    response = notion.databases.query(
        database_id=db_id,
        filter={
            "property": "Name",
            "title": {
                "equals": name
            }
        }
    )
    results = response.get("results", [])
    if not results:
        raise ValueError(f"No page with name '{name}' found in DB {db_id}")
    return results[0]

def extract_number(prop, default=0):
    if prop is None:
        return default
    if "rollup" in prop:
        return prop.get("rollup", {}).get("number", default) or default
    if "number" in prop:
        return prop.get("number", default) or default
    return default

def main():
    log("🚀 Starting Notion DB update")

    # Fetch SCORE page
    score_page = get_page_by_name(SCORE_DB_ID, TARGET_PAGE_NAME)
    s_props = score_page["properties"]

    score_exp = extract_number(s_props.get("EXP"))
    score_coins = extract_number(s_props.get("Coins"))
    log(f"🎮 SCORE → EXP: {score_exp}, Coins: {score_coins}")

    # Fetch MAIN page
    main_page = get_page_by_name(MAIN_DB_ID, TARGET_PAGE_NAME)
    m_props = main_page["properties"]

    main_xp = extract_number(m_props.get("XP"))
    main_coins = extract_number(m_props.get("coins"))
    log(f"📊 MAIN (before) → XP: {main_xp}, coins: {main_coins}")

    # Calculate new totals
    new_xp = main_xp + score_exp
    new_coins = main_coins + score_coins

    # Update MAIN page
    notion.pages.update(
        page_id=main_page["id"],
        properties={
            "XP": {"number": new_xp},
            "coins": {"number": new_coins}
        }
    )
    log(f"✅ Updated MAIN → XP: {new_xp}, coins: {new_coins}")

    # Placeholder for future DB updates
    update_additional_db()

    log("🎯 Update completed.\n")

def update_additional_db():
    # Placeholder function for future DB logic
    pass

if __name__ == "__main__":
    main()
print("✅ Script completed successfully")
