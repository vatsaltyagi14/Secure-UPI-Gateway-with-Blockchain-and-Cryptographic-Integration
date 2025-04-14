import socket
import json
import hashlib
from datetime import datetime

BANK_IP = "127.0.0.1"
BANK_PORT = 5000

def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()

def send_to_bank(data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((BANK_IP, BANK_PORT))
        s.sendall(json.dumps(data).encode())
        return json.loads(s.recv(4096).decode())

def send_to_upi(upi_ip, port, data):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((upi_ip, port))
            s.sendall(json.dumps(data).encode())
            return json.loads(s.recv(4096).decode())
    except Exception as e:
        return {"status": "error", "message": str(e)}

def register_user():
    print("[USER] === Register User ===")
    name = input("Name: ")
    mobile = input("Mobile: ")
    pin = input("PIN: ")
    hashed_pin = hash_pin(pin)
    balance = input("Balance: ")
    timestamp = datetime.now().isoformat()

    data = {
        "type": "register_user",
        "name": name,
        "mobile": mobile,
        "pin": hashed_pin,
        "balance": balance,
        "timestamp": timestamp
    }

    res = send_to_bank(data)
    if res["status"] == "success":
        print("Acknowldgement from Bank: User registered")
        print(f"[USER] UID: {res['uid']}")
        print(f"[USER] MMID: {res['mmid']}")
    else:
        print("[USER] Registration failed:", res.get("message"))

def make_payment():
    print("\n[USER] === Simulate QR Scan ===")
    qr = input("Paste QR content (format: VMID:PORT): ").strip()
    if ':' not in qr:
        print("[USER] Invalid QR format.")
        return
    vmid, port_str = qr.split(':')
    port = int(port_str)

    mmid = input("Your MMID: ")
    pin = input("Your PIN: ")
    hashed_pin = hash_pin(pin)

    amount = input("Amount to pay: ")

    tx = {
        "type": "transaction",
        "vmid": vmid,
        "mmid": mmid,
        "pin": hashed_pin,
        "amount": amount
    }

    res = send_to_upi("127.0.0.1", port, tx)
    print("Acknowldgement from Bank:")
    print(f"[USER] Result: {res}")

def main():
    while True:
        print("\n=== USER MENU ===")
        print("1. Register User")
        print("2. Make Payment (QR Scan)")
        print("3. Exit")
        choice = input("Choose: ")

        if choice == "1":
            register_user()
        elif choice == "2":
            make_payment()
        elif choice == "3":
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
