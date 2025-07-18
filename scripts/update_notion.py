import os
import datetime
from notion_client import Client

# only load .env locally
if not os.getenv("CI"):  # CI=true is automatically set in GitHub Actions
    from dotenv import load_dotenv
    load_dotenv()

# Read env vars
NOTION_API_KEY = os.getenv("NOTION_API_KEY", "").strip()
SCORE_DB_ID = os.getenv("SCORE_DB_ID", "").strip()
MAIN_DB_ID = os.getenv("MAIN_DB_ID", "").strip()

if not NOTION_API_KEY:
    raise RuntimeError("❌ NOTION_API_KEY is missing")
if not SCORE_DB_ID or not MAIN_DB_ID:
    raise RuntimeError("❌ SCORE_DB_ID or MAIN_DB_ID is missing")

notion = Client(auth=NOTION_API_KEY)

# Constants
MENU_PAGE_NAME = "Total"
SCORE_PAGE_NAME ="Score" 
SCORE_TITLE_PROPERTY = "Scores"
MAIN_TITLE_PROPERTY = "Dashboard"


def log(message):
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("[%Y-%m-%d %H:%M:%S UTC]")
    os.makedirs("logs", exist_ok=True)
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
    return results[0] if results else None


def get_property(page, prop_name):
    prop = page["properties"].get(prop_name, {})
    if prop.get("type") == "rollup":
        return prop.get("rollup", {}).get("number", 0) or 0
    if prop.get("type") == "number":
        return prop.get("number", 0) or 0
    return 0


def update_property(page_id, prop_name, value):
    notion.pages.update(
        page_id=page_id,
        properties={prop_name: {"number": value}}
    )


def main():
    log("⚡ Starting Notion update script")
    log("🚀 Starting Notion DB update")

    # Get pages
    score_page = get_page_by_name(SCORE_DB_ID, SCORE_TITLE_PROPERTY,SCORE_PAGE_NAME)
    main_page = get_page_by_name(MAIN_DB_ID, MAIN_TITLE_PROPERTY,MENU_PAGE_NAME)

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
    try:
        main()
    except Exception as e:
        log(f"🔥 Script crashed: {e}")
        raise
