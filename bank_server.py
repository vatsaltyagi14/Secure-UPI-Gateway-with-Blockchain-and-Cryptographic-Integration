import asyncio
import hashlib
import json
from datetime import datetime

users_by_mmid = {}
merchants_by_mid = {}
ledger = []  # lock-free, append-only blockchain


def sha256_full(data):
    return hashlib.sha256(data.encode()).hexdigest()

def sha256_16(data):
    return sha256_full(data)[:16]

def get_latest_block_hash():
    if not ledger:
        return "GENESIS"
    last = ledger[-1]
    content = f"{last['txn_id']}{last['uid']}{last['mid']}{last['amount']}{last['timestamp']}{last['prev_hash']}"
    return sha256_full(content)

def add_block(uid, mid, amount):
    timestamp = datetime.now().isoformat()
    txn_id = sha256_full(uid + mid + str(amount) + timestamp)
    prev_hash = get_latest_block_hash()
    block = {
        "txn_id": txn_id,
        "uid": uid,
        "mid": mid,
        "amount": amount,
        "timestamp": timestamp,
        "prev_hash": prev_hash
    }
    ledger.append(block)
    print(f"[BLOCKCHAIN] ⛓️ Block added: {txn_id[:10]}...")

def verify_chain():
    print("\n[VERIFY] Verifying Blockchain Integrity...")
    prev_hash = "GENESIS"
    for i, block in enumerate(ledger):
        content = f"{block['txn_id']}{block['uid']}{block['mid']}{block['amount']}{block['timestamp']}{block['prev_hash']}"
        computed_hash = sha256_full(content)
        if block['prev_hash'] != prev_hash:
            print(f"[VERIFY] Tampering at block {i}")
            return False
        prev_hash = computed_hash
    print("[VERIFY] All blocks valid.")
    return True

async def handle_registration(data):
    if data["type"] == "register_user":
        uid = sha256_16(data["name"] + data["mobile"] + data["timestamp"])
        mmid = sha256_16(uid + data["mobile"])
        pin_hash = sha256_full(data["pin"])
        user = {
            "uid": uid,
            "mmid": mmid,
            "name": data["name"],
            "mobile": data["mobile"],
            "pin_hash": pin_hash,
            "balance": float(data["balance"])
        }
        users_by_mmid[mmid] = user
        print(f"Acknowledgement: [BANK]  Registered UID={uid}, MMID={mmid}")
        return {"status": "success", "uid": uid, "mmid": mmid}

    elif data["type"] == "register_merchant":
        mid = sha256_16(data["name"] + data["password"] + data["timestamp"])
        pass_hash = sha256_full(data["password"])
        merchant = {
            "mid": mid,
            "name": data["name"],
            "password_hash": pass_hash,
            "balance": float(data["balance"])
        }
        merchants_by_mid[mid] = merchant
        print(f"Acknowledgement: [BANK]  Registered MID={mid}")
        return {"status": "success", "mid": mid}

    return {"status": "error", "message": "Unknown registration"}

async def handle_transaction(data):
    mmid = data["mmid"]
    pin = data["pin"]
    amount = float(data["amount"])
    vmid = data["vmid"]

    print(f"Acknowledgement: [BANK] TX: MMID={mmid} → VMID={vmid} Amt={amount}")

    user = users_by_mmid.get(mmid)
    if not user:
        return {"status": "fail", "message": "Invalid MMID"}

    hashed_pin = sha256_full(pin)
    if hashed_pin != user["pin_hash"]:
        return {"status": "fail", "message": "Wrong PIN"}

    if user["balance"] < amount:
        return {"status": "fail", "message": "Insufficient funds"}

    user["balance"] -= amount
    add_block(uid=user["uid"], mid=vmid, amount=amount)
    return {"status": "success", "message": "Transaction successful"}

async def process_request(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"\n[BANK]  Connected: {addr}")

    try:
        data = await reader.read(4096)
        msg = json.loads(data.decode())

        if msg["type"].startswith("register"):
            res = await handle_registration(msg)
        elif msg["type"] == "transaction":
            res = await handle_transaction(msg)
        elif msg["type"] == "verify_chain":
            valid = verify_chain()
            res = {"status": "verified" if valid else "tampered"}
        else:
            res = {"status": "fail", "message": "Unknown type"}

        response = json.dumps(res).encode()
        writer.write(response)
        await writer.drain()
    except Exception as e:
        print(f"[BANK]  Error: {e}")
        writer.write(json.dumps({"status": "error", "message": str(e)}).encode())
        await writer.drain()
    finally:
        writer.close()
        await writer.wait_closed()

async def start_server():
    server = await asyncio.start_server(process_request, '0.0.0.0', 5000)
    addr = server.sockets[0].getsockname()
    print(f"[BANK]  Async server running @ {addr}")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(start_server())
