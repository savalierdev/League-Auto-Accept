from lcu_driver import Connector
import json
import asyncio

connector = Connector()
searching_printed = False  # Bayrak değişkeni

async def check_match_status(connection):
    global searching_printed  # Bayrak değişkenini global olarak kullan
    try:
        matchstatus = await connection.request("get", "/lol-matchmaking/v1/search")
        matchstatus_json = await matchstatus.json()
        search_state = matchstatus_json.get("searchState")
        if search_state == "Found":
            searching_printed = False  # Bayrağı sıfırla
            return True
        elif search_state == "Searching":
            if not searching_printed:
                print("Searching for match")
                searching_printed = True  # Bayrağı ayarla
            return False
    except Exception as e:
        print(e)
        return None

async def match_search_loop(connection):
    while True:
        check = await check_match_status(connection)
        if check is None:
            await asyncio.sleep(5)  # Yeniden bağlanmadan önce biraz bekle
            continue  # Döngüyü tekrar başlat
        if check == True:
            print("Match Found")
            try:
                await connection.request("post", "/lol-matchmaking/v1/ready-check/accept")
                print("Match accepted")
            except Exception as e:
                print(f"Failed to accept match: {e}")
            await asyncio.sleep(5)  # Maç kabul edildikten sonra biraz bekle
        await asyncio.sleep(1)

@connector.ready
async def connect_client(connection):
    print(f"Client Port : {connection.port}")
    print(f"Client Process ID : {connection.pid}")
    print(f"Client URL : {connection.address}")
    print(f"Client Auth : {connection.auth_key}")
    print("LCU API is ready")
    await match_search_loop(connection)

@connector.ws.register('/lol-matchmaking/v1/search', event_types=('UPDATE',))
async def on_search_update(connection, event):
    await match_search_loop(connection)

connector.start()
