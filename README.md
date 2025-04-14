# Quantum-Secure UPI Gateway with Blockchain and Cryptographic Integration

This project implements a simulated centralized UPI (Unified Payments Interface) Payment Gateway with advanced cryptographic techniques to ensure secure digital transactions. The system integrates Blockchain for transaction integrity, Lightweight Cryptography (LWC) for efficient encryption, and a simulation of Shor’s Algorithm to demonstrate potential vulnerabilities in classical cryptographic mechanisms such as PINs and UIDs.


## Overview

The project simulates a secure digital payment system involving three core entities:
1. `Bank Server` – Handles user and merchant registration, transaction verification, and maintains the blockchain.
2. `UPI Machine` – Represents a merchant terminal that generates encrypted QR codes and processes user payment requests.
3. `User Client` – Acts as the user device to initiate payments via MMID and PIN by scanning merchant QR codes.

Additionally, the project includes a classical simulation of **Shor's Algorithm** to demonstrate the risk that quantum computing poses to current PIN- and UID-based authentication systems.

## System Architecture

- **Blockchain**: Used by the Bank Server to store all valid transactions immutably with chained hashes.
- **Lightweight Cryptography (LWC)**: Used in the UPI machine to encrypt Merchant IDs and generate Virtual Merchant IDs (VMID).
- **Quantum Cryptography Simulation**: Simulates breaking classical encryption with a simplified Shor’s Algorithm.
- **Socket Communication**: All entities communicate over TCP sockets on localhost.

## Project Structure

The project includes the following key components:

- `bank_server.py`: Implements the central banking server that handles user and merchant registration, transaction validation, and maintains a blockchain ledger to ensure transaction integrity.
- `upi_machine.py`: Simulates a merchant's UPI device. It handles merchant registration, generates encrypted QR codes using LWC (hashed MID), listens for user transactions, and forwards them to the bank.
- `user_client.py`: Simulates the user's side of the UPI transaction. Allows users to register with the bank, scan QR codes, and initiate transactions using MMID and PIN.
- `shor_attack.py`: A standalone script that simulates Shor’s Algorithm to factor synthetic PIN and UID patterns. Demonstrates vulnerabilities of classical cryptography under potential quantum threats.

## Technologies Used

- Python 3
- SHA-256 hashing
- Lightweight encryption inspired by the SPECK cipher
- Classical simulation of Shor's Algorithm (quantum period finding)
- QR code generation (`qrcode` Python library)
- TCP socket programming using `socket`, `asyncio`, and `threading`

# Run Instructions for Quantum-Secure UPI Gateway with Blockchain and Cryptographic Integration

Before starting, please ensure you have installed all required Python libraries using the provided requirements.txt file.

Run the following command in your terminal to install dependencies:

    pip install -r requirements.txt

---

## Step 1: Start the Bank Server

### Command:
    python3 bank_server.py

### Output:
- Server starts on port 5000.
- Ready to accept merchant and user registrations and transactions.

---

## Step 2: Start the UPI Machine (Merchant Side)

### Command:
    python3 upi_machine.py

### You will be prompted to enter:
- Merchant Name
- Password
- Initial Balance
- A unique port (e.g., 6001)

### Output:
- QR code saved as <merchant_name>_qr.png
- Listens for user payments on the specified port

---

## Step 3: Run the User Client

### Command:
    python3 user_client.py

### Menu Options:
1. Register User
2. Make Payment (QR Scan)
3. Exit

#### Option 1: Register User
- Inputs: Name, Mobile, PIN, Balance
- Output: UID and MMID

#### Option 2: Make Payment
- Inputs:
  - QR Content (from QR code, e.g., fa12b45f3a6e1dcd:6001)
  - MMID
  - PIN
  - Amount
- Transaction forwarded to bank
- Result displayed to user

---

## Optional Step: Run Shor's Algorithm Simulation (Quantum Attack Demo)

### Command:
    python3 shor_attack.py

### Menu:
1. Attack PIN
2. Attack UID
3. Exit

- Demonstrates classical simulation of quantum vulnerability via integer factorization.

---

## Sample Terminal Layout

| Terminal | Script             | Role              |
|----------|--------------------|-------------------|
| 1        | bank_server.py     | Bank server       |
| 2        | upi_machine.py     | Merchant/UPI terminal |
| 3        | user_client.py     | User actions      |
| 4 (opt.) | shor_attack.py     | Quantum attack demo |

---

## QR Code Usage

After merchant setup, you will see a file like:

    ShopMart_qr.png

It contains:

    fa12b45f3a6e1dcd:6001

This text should be pasted exactly into the user client during payment.

---
