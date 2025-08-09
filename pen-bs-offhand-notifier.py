import requests
import time
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional
from plyer import notification

@dataclass
class GameItem:
    id: int
    enhancement: int = 0
    name: str = ""

@dataclass
class MarketItemOrder:
    buyers: int = 0
    sellers: int = 0
    price: Decimal = Decimal("0.0")

@dataclass
class MarketItem:
    id: int
    enhancement: int
    name: str
    orders: List[MarketItemOrder]

def parse_market_item(data: dict, item_name: str) -> MarketItem:
    try:
        orders = [
            MarketItemOrder(
                buyers=o.get("buyers", 0),
                sellers=o.get("sellers", 0),
                price=Decimal(str(o["price"]))
            )
            for o in data.get("orders", [])
        ]
    except Exception as e:
        print(f"Error in parse_market_item for {item_name}: ({type(e).__name__}) {e}")
        print(f"Received data: {data}")
        raise

    return MarketItem(
        id=data["id"],
        enhancement=data.get("sid", 0),
        name=item_name,
        orders=orders
    )

def fetch_market_item(game_item: GameItem, region="eu") -> Optional[MarketItem]:
    url = f"https://api.arsha.io/v2/{region}/GetBiddingInfoList?lang=en"
    payload = [{"id": game_item.id, "sid": game_item.enhancement}]
    headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()

    if not data:
        return None

    return parse_market_item(data, game_item.name)

def check_waitlist(region: str, items_to_check: List[GameItem], price_cap: int = 80_000_000_000):
    url = f"https://api.arsha.io/v2/{region}/GetWorldMarketWaitList"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        waitlist = response.json()
    except Exception as e:
        print(f"Failed to fetch waitlist: ({type(e).__name__}) {e}")
        return

    for entry in waitlist:
        entry_id = entry.get("id")
        sid = entry.get("sid", 0)
        price = int(entry.get("price", 0))
        for item in items_to_check:
            if item.id == entry_id and item.enhancement == sid:
                if price <= price_cap:
                    msg = f"{item.name} (+{item.enhancement}) listed at {price:,} Silver!"
                    print(f"⚠️  WAITLIST: {msg}")
                    notification.notify(
                        title="🔔 Black Desert Market Alert",
                        message=msg,
                        app_name="BDO Market Watch",
                        timeout=10
                    )

items_to_check = [
    GameItem(id=735001, enhancement=20, name="Blackstar Shield"),
    GameItem(id=735003, enhancement=20, name="Blackstar Talisman"),
    GameItem(id=735002, enhancement=20, name="Blackstar Dagger"),
    GameItem(id=735004, enhancement=20, name="Blackstar Ornamental"),
    GameItem(id=735005, enhancement=20, name="Blackstar Trinket"),
    GameItem(id=735006, enhancement=20, name="Blackstar Horn Bow"),
    GameItem(id=735007, enhancement=20, name="Blackstar Kunai"),
    GameItem(id=735008, enhancement=20, name="Blackstar Shuriken"),
    GameItem(id=735009, enhancement=20, name="Blackstar Vambrace"),
    GameItem(id=735010, enhancement=20, name="Blackstar Noble Sword"),
    GameItem(id=735011, enhancement=20, name="Blackstar Ra'ghon"),
    GameItem(id=735012, enhancement=20, name="Blackstar Vitclari"),
    GameItem(id=735013, enhancement=20, name="Blackstar Haladie"),
    GameItem(id=735014, enhancement=20, name="Blackstar Quotarum"),
    GameItem(id=735015, enhancement=20, name="Blackstar Mareca"),
    GameItem(id=735016, enhancement=20, name="Blackstar Shard"),
    GameItem(id=735017, enhancement=20, name="Blackstar Do Stave"),
    GameItem(id=735018, enhancement=20, name="Blackstar Binyeo Knife"),
    GameItem(id=735019, enhancement=20, name="Blackstar Gravity Cores"),
    GameItem(id=735020, enhancement=20, name="Blackstar Gombangdae"),
    GameItem(id=735021, enhancement=20, name="Blackstar Shotgun"),
    GameItem(id=735022, enhancement=20, name="Blackstar Gourd Bottle"),
]

region = "eu"
print("📡 Starting market monitor...")
while True:
    check_waitlist(region, items_to_check)
    time.sleep(60)
