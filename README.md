# Rajendra Gruh Vastu Bhandar - Modern POS

A desktop Point of Sale (POS) application built with Python and CustomTkinter for a modern interface. This project supports billing, inventory management, customer registry, profit reporting, and voice-assisted item entry.

## Features

- Modern GUI with `customtkinter` and `tkinter`
- Billing module with cart management and checkout
- Inventory manager for items, cost price, selling price, and stock
- Customer registry with name and phone number
- Profit dashboard showing total net profit
- Voice input for adding items via speech recognition
- Local `sqlite3` database storage

## Files

- `index.py` - Main application source code
- `README.md` - Project documentation
- `rajendra_gruh_vastu.db` - SQLite database used by the app 

## Requirements

- Python 3.8+
- `customtkinter`
- `speechrecognition`
- `pyttsx3`
- `sqlite3` (built-in)
- `pyaudio` or another microphone backend for speech recognition

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Dinesh04-prog/python-project.git
cd python-project
```

2. Install dependencies:

```bash
pip install customtkinter speechrecognition pyttsx3 pyaudio
```

> On Windows, if `pyaudio` fails to install via pip, use the appropriate wheel from [https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio).

## Running the App

Run the main script:

```bash
python index.py
```

## How to Use

1. Enter a customer name and phone number on the login overlay.
2. Use the sidebar to switch between:
   - Billing
   - Inventory
   - Profit & Loss
   - Customers
3. In Billing, add items manually or use the voice mic button to add items with speech.
4. Checkout to save sales data to the local SQLite database.

## Notes

- The app stores data in `rajendra_gruh_vastu.db`.
- Database files are local and contain inventory/customers/sales data.
- If you prefer not to track the `.db` files in Git, add `*.db` to `.gitignore`.

## License

This repository does not include a license file. Add a license if you want to make the project open source.
