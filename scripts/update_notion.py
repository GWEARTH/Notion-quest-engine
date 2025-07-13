import os
import datetime
from notion_client import Client
from dotenv import load_dotenv

# Load env vars
load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_API_KEY", "").strip()
SCORE_DB_ID = os.getenv("SCORE_DB_ID", "").strip()
MAIN_DB_ID = os.getenv("MAIN_DB_ID", "").strip()

# Constants
TARGET_PAGE_NAME = "Null"
SCORE_TITLE_PROPERTY = "Scores"
MAIN_TITLE_PROPERTY = "Dashboard"

notion = Client(auth=NOTION_TOKEN)

def log(message):
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("[%Y-%m-%d %H:%M:%S UTC]")
    with open("logs/update.log", "a") as f:
        f.write(f"{timestamp} {message}\n")
    print(message)

def get_page_by_name(db_id, title_property, page_name):
    response = notion.databases.query(
        database_id=db_id,
        filter={
            "property": title_property,
            "title": {
                "equals": page_name
            }
        }
    )
    results = response.get("results", [])
    if results:
        return results[0]
    return None

def get_property(page, prop_name):
    props = page["properties"]
    prop = props.get(prop_name, {})
    if prop.get("type") == "rollup":
        return prop.get("rollup", {}).get("number", 0) or 0
    elif prop.get("type") == "number":
        return prop.get("number", 0) or 0
    else:
        return 0

def update_property(page_id, prop_name, value):
    notion.pages.update(
        page_id=page_id,
        properties={
            prop_name: {
                "number": value
            }
        }
    )

def main():
    log("⚡ Starting Notion update script")
    os.makedirs("logs", exist_ok=True)

    # Get pages
    log("🚀 Starting Notion DB update")
    score_page = get_page_by_name(SCORE_DB_ID, SCORE_TITLE_PROPERTY, TARGET_PAGE_NAME)
    main_page = get_page_by_name(MAIN_DB_ID, MAIN_TITLE_PROPERTY, TARGET_PAGE_NAME)

    if not score_page or not main_page:
        log("❌ Could not find one or both pages.")
        return

    # Get XP & Coins from Score DB
    xp_from_score = get_property(score_page, "EXP")
    coins_from_score = get_property(score_page, "Coins")

    log(f"🔷 XP from Score DB: {xp_from_score}")
    log(f"🔷 Coins from Score DB: {coins_from_score}")

    # Get current XP & Coins from Main DB
    xp_from_main = get_property(main_page, "XP")
    coins_from_main = get_property(main_page, "Coins")

    log(f"🔷 XP from Main DB: {xp_from_main}")
    log(f"🔷 Coins from Main DB: {coins_from_main}")

    # Add them
    new_xp = xp_from_main + xp_from_score
    new_coins = coins_from_main + coins_from_score

    log(f"✅ New XP: {new_xp}")
    log(f"✅ New Coins: {new_coins}")

    # Update Main DB
    update_property(main_page["id"], "XP", new_xp)
    update_property(main_page["id"], "Coins", new_coins)

    log("🎉 Successfully updated Main DB.")

if __name__ == "__main__":
    main()
