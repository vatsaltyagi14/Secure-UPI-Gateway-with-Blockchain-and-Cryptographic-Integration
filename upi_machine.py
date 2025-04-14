import socket
import json
import hashlib
import qrcode
from datetime import datetime
import threading

BANK_IP = "127.0.0.1"
BANK_PORT = 5000

import random



WORD_SIZE = 32
MASK_VAL = 0xFFFFFFFF
ALPHA = 8
BETA = 3
ROUNDS = 27

def rol(x, r):
    return ((x << r) & MASK_VAL) | (x >> (WORD_SIZE - r))

def ror(x, r):
    return ((x >> r) | (x << (WORD_SIZE - r))) & MASK_VAL

def speck_key_schedule(key):
    # Key should be 4 words (128-bit key for 64-bit block)
    l = key[:-1]
    k = [key[-1]]
    for i in range(ROUNDS - 1):
        l.append(((k[i] + ror(l[i], ALPHA)) & MASK_VAL) ^ i)
        k.append(rol(k[i], BETA) ^ l[i + 1])
    return k

def speck_encrypt(plain, round_keys):
    x, y = plain
    for k in round_keys:
        x = (ror(x, ALPHA) + y) & MASK_VAL ^ k
        y = rol(y, BETA) ^ x
    return x, y

def speck_decrypt(cipher, round_keys):
    x, y = cipher
    for k in reversed(round_keys):
        y = ror(y ^ x, BETA)
        x = (rol((x ^ k) - y & MASK_VAL, ALPHA))
    return x, y

def text_to_blocks(text):
    b = text.encode("utf-8").ljust(8, b'\x00')  # pad to 8 bytes
    return int.from_bytes(b[:4], "big"), int.from_bytes(b[4:], "big")

def blocks_to_text(blocks):
    b = blocks[0].to_bytes(4, "big") + blocks[1].to_bytes(4, "big")
    return b.rstrip(b'\x00').decode("utf-8")

def generate_key():
    return [random.getrandbits(WORD_SIZE) for _ in range(4)]

def encrypt_mid_to_vmid(mid, round_keys):
    pt_blocks = text_to_blocks(mid[:8])  # MID trimmed/padded to 8 chars
    ct = speck_encrypt(pt_blocks, round_keys)
    return f"{ct[0]:08x}{ct[1]:08x}"

def decrypt_vmid_to_mid(vmid, round_keys):
    x = int(vmid[:8], 16)
    y = int(vmid[8:], 16)
    dt_blocks = speck_decrypt((x, y), round_keys)
    return blocks_to_text(dt_blocks)

def speck_fake_encrypt(mid):
    return hashlib.sha256(mid.encode()).hexdigest()[:16]

def generate_qr(vmid, port, merchant_name):
    qr_data = f"{vmid}:{port}"
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    filename = f"{merchant_name}_qr.png"
    img.save(filename)
    print(f"[UPI] QR saved as {filename} with data: {qr_data}")

def send_to_bank(data):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((BANK_IP, BANK_PORT))
            s.sendall(json.dumps(data).encode())
            response = s.recv(4096)
            return json.loads(response.decode())
    except Exception as e:
        return {"status": "error", "message": str(e)}

def handle_user(conn):
    try:
        data = conn.recv(4096)
        tx = json.loads(data.decode())
        print(f"[UPI] Received from User: {tx["mmid"]}")
        result = send_to_bank(tx)
        conn.sendall(json.dumps(result).encode())
        print("[UPI] Sent result to User")
    except Exception as e:
        conn.sendall(json.dumps({"status": "error", "message": str(e)}).encode())

def start_listener(port):
    print(f"[UPI] Listening on port {port}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", port))
        s.listen()
        while True:
            conn, _ = s.accept()
            threading.Thread(target=handle_user, args=(conn,)).start()

def main():
    print("\n=== UPI Machine: Merchant Setup ===")
    name = input("Merchant Name: ")
    password = input("Password: ")
    balance = input("Balance: ")
    port = int(input("Choose a unique UPI port (e.g. 6001, 6002...): "))
    timestamp = datetime.now().isoformat()

    # Register merchant
    data = {
        "type": "register_merchant",
        "name": name,
        "password": password,
        "balance": balance,
        "timestamp": timestamp
    }

    response = send_to_bank(data)
    if response["status"] == "success":
        print("Acknowldgement from Bank: Merchant registered")
        mid = response["mid"]
        vmid = speck_fake_encrypt(mid)
        generate_qr(vmid, port, name)
        start_listener(port)
    else:
        print("[UPI] Registration failed:", response.get("message", "Unknown error"))

if __name__ == "__main__":
    main()
