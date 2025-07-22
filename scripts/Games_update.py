from notion_client import Client
import os

# 🔷 Config
NOTION_API_KEY = os.getenv("NOTION_API_KEY").strip()
GAMES_PAGE_ID = os.getenv("STORE_GAMES_ID").strip()
STATS_DB_ID = os.getenv("MAIN_DB_ID").strip()

GAMES_TIME_LEFT = "Time left"
GAMES_COINS_SUB = "Coins to be  substracted"
GAMES_VISIBILITY = "Visibilty"
STATS_COINS = "Coins"  # adjust if needed

notion = Client(auth=NOTION_API_KEY)

def get_child_databases(page_id):
    dbs = []
    children = notion.blocks.children.list(page_id)["results"]
    for block in children:
        if block["type"] == "child_database":
            dbs.append(block["id"])
    return dbs

def get_current_stats_coins():
    # Assuming only one row in STATS DB
    stats_pages = notion.databases.query(database_id=STATS_DB_ID)["results"]
    if not stats_pages:
        raise Exception("No pages found in STATS database.")
    page = stats_pages[0]
    props = page["properties"]
    coins = props[STATS_COINS]["number"]
    return page["id"], coins

def update_stats_coins(stats_page_id, new_coins):
    notion.pages.update(
        page_id=stats_page_id,
        properties={STATS_COINS: {"number": new_coins}}
    )

def process_games():
    print(f"🔎 Checking GAMES page: {GAMES_PAGE_ID}")
    dbs = get_child_databases(GAMES_PAGE_ID)
    if not dbs:
        print("❌ No child databases found under GAMES page.")
        return
    print(f"📚 Found {len(dbs)} child databases.")
    
    stats_page_id, current_coins = get_current_stats_coins()
    print(f"💰 Current STATS coins: {current_coins}")

    for db_id in dbs:
        print(f"\n--- Checking database: {db_id} ---")
        pages = notion.databases.query(database_id=db_id)["results"]
        
        for page in pages:
            props = page["properties"]

            time_left = props.get(GAMES_TIME_LEFT, {}).get("formula", {}).get("number", None)
            coins_to_sub = props.get(GAMES_COINS_SUB, {}).get("formula", {}).get("number", 0)

            if time_left is None:
                print(f"⏳ Skipping page {page['id']}: Time left not found.")
                continue

            if time_left != 0:
                print(f"⏳ Page {page['id']} has Time left = {time_left} > 0")
                continue

            # time_left == 0 → proceed
            print(f"✅ Page {page['id']} → Time left = 0 → Processing.")

            new_coins = current_coins - coins_to_sub
            if new_coins < 0:
                print(f"⚠️ Coins went below 0 → setting negative balance.")
            print(f"💰 Updating STATS coins: {current_coins} - {coins_to_sub} = {new_coins}")

            update_stats_coins(stats_page_id, new_coins)

            # Update the page → set Visibility to unchecked
            notion.pages.update(
                page_id=page["id"],
                properties={
                    GAMES_VISIBILITY: {"checkbox": False}
                }
            )

            print(f"👀 Visibility unchecked for page {page['id']}.")

            # Update current_coins in memory so subsequent pages deduct correctly
            current_coins = new_coins

if __name__ == "__main__":
    process_games()
