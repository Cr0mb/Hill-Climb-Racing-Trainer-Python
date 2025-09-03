<img width="1277" height="1023" alt="image" src="https://github.com/user-attachments/assets/a1953cbc-91b0-4e31-b0ab-7989e18c76b0" />


# Hill Climb Racing Trainer

A simple Python-based memory editor for **Hill Climb Racing** that allows you to set **Money** and **Diamonds** and enables an **unlimited gas feature**. Built using `ctypes` for direct memory access and `psutil` for process management on Windows.

---

## Features

* **Unlimited Gas:** Keeps your gas constantly at 100.
* **Set Money:** Modify your in-game money at runtime.
* **Set Diamonds:** Modify your in-game diamonds at runtime.

---

## Requirements

* Windows OS
* Python 3.8+
* `psutil` library

Install dependencies with:

```bash
pip install psutil
```

---

## Usage

1. Run the trainer with Python:

```bash
python hillclimbing.py
```

2. Select an option from the menu:

```
=== Hill Climb Racing Trainer ===
1. Set Money
2. Set Diamonds
3. Exit
```

3. Enter the desired value for Money or Diamonds.

4. Enjoy unlimited gas while playing.

---

## How It Works

* Attaches to `HillClimbRacing.exe` using Windows API (`OpenProcess`, `ReadProcessMemory`, `WriteProcessMemory`).
* Uses **pointer offsets** to locate memory addresses for Money, Diamonds, and Gas.
* A separate **thread constantly freezes Gas** at 100 using a high-frequency update loop.
* Menu allows dynamic modification of in-game values while the game is running.

---
