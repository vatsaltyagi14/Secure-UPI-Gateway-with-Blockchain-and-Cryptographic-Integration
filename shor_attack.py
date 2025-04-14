import math
import random


def shors_classical(N):
    print(f"[SHOR] Simulating quantum factoring of N = {N}")

    if N % 2 == 0:
        return 2

    a = random.randint(2, N - 2)
    print(f"[SHOR] Random base a = {a}")

    g = math.gcd(a, N)
    if g != 1:
        print(f"[SHOR] Nontrivial factor found by GCD: {g}")
        return g

    r = find_order(a, N)
    if r is None or r % 2 != 0:
        print("[SHOR] Invalid order r")
        return None

    x = pow(a, r // 2, N)
    if x == N - 1:
        print("[SHOR] Trivial result: x == N - 1")
        return None

    p = math.gcd(x - 1, N)
    q = math.gcd(x + 1, N)

    if p * q == N:
        print(f"[SHOR] Quantum break success: {N} = {p} * {q}")
        return p, q

    print("[SHOR] Factorization failed")
    return None

def find_order(a, N):
    print("[SHOR] Searching for period r such that a^r mod N == 1...")
    for r in range(2, N):
        if pow(a, r, N) == 1:
            print(f"[SHOR] Order found: r = {r}")
            return r
    return None

def simulate_pin_attack():
    print("\n [QUANTUM ATTACK] Simulating Shor's Algorithm on 4-digit PIN hashed composite")
    pin = input("Enter 4-digit PIN: ")
    num = int(pin + pin)  # Double PIN pattern to simulate weak modulus
    print(f"Generated simulated N = {num}")
    result = shors_classical(num)
    if result:
        print(" Potential PIN breakdown via quantum factoring:", result)
    else:
        print(" PIN survived quantum factoring simulation.")

def simulate_uid_attack():
    print("\n [QUANTUM ATTACK] Simulating Shor's Algorithm on UID composite")
    uid = input("Enter UID segment (numeric): ")
    num = int(uid + uid[:3])  # Weak synthetic N
    print(f"Generated simulated N = {num}")
    result = shors_classical(num)
    if result:
        print(" Potential UID breakdown via quantum factoring:", result)
    else:
        print(" UID survived quantum factoring simulation.")

if __name__ == "__main__":
    print("\n=== Quantum Cryptographic Attack Simulation ===")
    print("1. Attack PIN")
    print("2. Attack UID")
    print("3. Exit")
    while True:
        choice = input("Choose: ")
        if choice == "1":
            simulate_pin_attack()
        elif choice == "2":
            simulate_uid_attack()
        elif choice == "3":
            break
        else:
            print("Invalid.")
