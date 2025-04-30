# 🚀 CafePOS Pro: E-Receipt Based POS System for Cafeteria

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green)

---

## 📝 Overview

> **CafePOS Pro** is a modern, digital Point-of-Sale (POS) system for the Fast NU Islamabad cafeteria.  
> It streamlines order management, generates e-receipts, and provides real-time transaction insights.  
> Built with **Python** and **Tkinter**, it features a user-friendly interface, customer history, admin controls, and automatic email receipts.

---

## ✨ Features

- **Intuitive GUI:** Clean, responsive interface built with Tkinter.
- **Menu Categories:** Hot/Cold Beverages, Breakfast, Lunch, Snacks—each with clickable item buttons.
- **Order Management:**
  - Add items to order with a click.
  - View and update current order in real time.
  - Reset order at any time.
- **Customer Lookup:**
  - Enter roll number or email to auto-fill and check history.
  - View last 3 transactions and total visits.
- **E-Receipt Generation:**
  - Auto-generates and saves receipts for every transaction in `/receipts/`.
  - Example receipt:

    ```txt
    NATIONAL UNIVERSITY - ISLAMABAD CAMPUS
    =============================================
    Date: 2025-04-30 13:58:32
    Customer: i245163@isb.nu.edu.pk
    ---------------------------------------------
    ITEM               QTY   PRICE   TOTAL
    ---------------------------------------------
    French Toast        1     700Rs    700Rs
    Pancakes            1     600Rs    600Rs
    ---------------------------------------------
                                    TOTAL: 1300.00Rs
    =============================================
    Thank you for your purchase!
           CafePOS Pro v1.0
    ```

- **Email Receipts:**
  - Sends receipts directly to the customer's university email (Gmail SMTP, configurable).
- **Admin Panel:**
  - User management: search, view, edit, delete users.
  - Transaction history: view all transactions, filter/search.
- **Data Persistence:**
  - All user and transaction data stored in `pos_users.json`.
  - Email config in `config.json`.

---

## ⚡ Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/your-username/E-reciept-based-Pos-system.git

# 2. Navigate to the project directory
cd E-reciept-based-Pos-system

# 3. Run the POS system
python3 E_Recipts_POS.py
```

---

## 🖥️ How the App Operates

### For Customers

1. **Start the Application:**
   - Double-click `E_Recipts_POS.py` or run it from terminal.
2. **Enter Your Details:**
   - Input your roll number (e.g., `i245163`) or university email.
   - Use **Auto-fill Email** to convert roll number to email.
   - Use **Check Customer** to view your last transactions.
3. **Place Your Order:**
   - Click menu items to add to your order.
   - Order summary updates in real time.
4. **Checkout:**
   - Click **Checkout** to complete your purchase.
   - Receipt is shown and emailed to you.
5. **Reset Order:**
   - Click **Reset Order** to clear your current order.

### For Admins

1. **Open Admin Panel:**
   - Click **Admin Panel** (top right).
2. **User Management:**
   - Search, view, edit, or delete users.
   - View user details and transaction history.
3. **Transaction History:**
   - Browse all transactions, filter/search as needed.

---

## 🗂️ Project Structure

```text
E-reciept-based-Pos-system/
├── E_Recipts_POS.py         # Main application (Tkinter GUI)
├── pos_users.json           # User and transaction data
├── config.json              # Email configuration
├── receipts/                # Saved receipt files
└── Readme.md                # Project documentation
```

---

## ⚙️ Configuration

To enable email receipts, update `config.json` with your sender Gmail address and app password:

```json
{
    "email": "your-email@gmail.com",
    "password": "your-app-password"
}
```

> **Note:** Use an [App Password](https://support.google.com/accounts/answer/185833) for Gmail if 2FA is enabled.

---

## 🛠️ Requirements

- Python 3.x
- Tkinter (usually included with Python)
- Internet connection for email sending (Gmail SMTP)

---

## 🧑‍💻 Example: Adding an Item to Order (Python)

```python
# Add item to current order
def add_to_order(self, item):
    name = item['name']
    if name in self.current_order:
        self.current_order[name]['quantity'] += 1
    else:
        self.current_order[name] = {'price': item['price'], 'quantity': 1}
    self.update_order_display()
```

---

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

---

## 📬 Contact

For questions or feedback, contact the maintainer: [ahsanxhah056@gmail.com](mailto:ahsanxhah056@gmail.com)
