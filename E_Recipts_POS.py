import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog, filedialog
import json
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import csv
import sys
import threading

class CafeteriaPOS:
    def __init__(self, root):
        self.root = root
        self.root.title("CafePOS Pro - NUCES Islamabad")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f5f5f5')

        # Initialize data storage
        self.users_file = "pos_users.json"
        self.config_file = "config.json"
        self.users = self.load_users()
        self.email_config = self.load_email_config()
        self.current_order = {}
        self.current_user = None

        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()

        # Create GUI components
        self.create_widgets()
        self.create_menu_grid()
        self.create_admin_button()

    def configure_styles(self):
        self.style.configure('TFrame', background='#f5f5f5')
        self.style.configure('Header.TLabel', font=('Helvetica', 15, 'bold'), foreground='#2c3e50')
        self.style.configure('Subheader.TLabel', font=('Helvetica', 10), foreground='#7f8c8d')
        self.style.configure('Item.TButton', 
                       font=('Arial', 34, 'bold'),  # Increased from 24 to 34
                       width=22, 
                       padding=18,  # Increased from 10 to 18
                       borderwidth=1, 
                       relief='raised')
        self.style.configure('Total.TLabel', font=('Helvetica', 15, 'bold'), foreground='#c0392b')
        self.style.configure('TButton', font=('Arial', 10), padding=5)
        self.style.configure('Admin.TButton', font=('Arial', 10), padding=5, foreground='white', background='#e74c3c')
    
        self.style.map('Item.TButton',
                      foreground=[('active', 'white'), ('!active', 'white')],
                      background=[('active', '#3498db'), ('!active', '#2980b9')])
        self.style.map('TButton',
                      foreground=[('active', 'white'), ('!active', 'white')],
                      background=[('active', '#27ae60'), ('!active', '#2ecc71')])
        self.style.map('Admin.TButton',
                      foreground=[('active', 'white'), ('!active', 'white')],
                      background=[('active', '#c0392b'), ('!active', '#e74c3c')])

    def load_users(self):
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r') as f:
                return json.load(f)
        return {}

    def load_email_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {"email": "", "password": ""}

    def save_users(self):
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)

    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding=(15, 15, 15, 15))
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Customer Info Frame
        customer_frame = ttk.Frame(main_frame, padding=10, relief='ridge', borderwidth=2)
        customer_frame.grid(row=0, column=0, columnspan=4, sticky='ew', pady=(0, 15))

        ttk.Label(customer_frame, text="Fast NUCES Islamabad POS System", style='Header.TLabel').grid(row=0, column=0, columnspan=4, sticky='w')
        ttk.Label(customer_frame, text="Enter Roll Number:", style='Subheader.TLabel').grid(row=1, column=0, sticky='w')
        
        self.customer_id = ttk.Entry(customer_frame, width=25, font=('Arial', 11))
        self.customer_id.grid(row=1, column=1, padx=5, sticky='w')
        
        ttk.Button(customer_frame, text="Check Customer", command=self.check_customer).grid(row=1, column=2, padx=5)
        ttk.Button(customer_frame, text="Auto-fill Email", command=self.convert_to_email).grid(row=1, column=3, padx=5)

        # Menu Frame
        menu_frame = ttk.Frame(main_frame, padding=10)
        menu_frame.grid(row=1, column=0, columnspan=3, sticky='nsew')

        # Order Frame
        order_frame = ttk.Frame(main_frame, padding=15, relief='ridge', borderwidth=2)
        order_frame.grid(row=1, column=3, rowspan=2, sticky='nsew', padx=(15, 0))

        # Order Header
        ttk.Label(order_frame, text="Current Order", style='Header.TLabel').pack(anchor='w')
        
        # Order Display
        self.order_text = scrolledtext.ScrolledText(order_frame, width=40, height=20, 
                                                  font=('Consolas', 10), wrap=tk.WORD,
                                                  padx=10, pady=10, bd=0)
        self.order_text.pack(fill=tk.BOTH, expand=True, pady=(5, 10))

        # Total Label
        total_frame = ttk.Frame(order_frame)
        total_frame.pack(fill=tk.X, pady=(5, 10))
        ttk.Label(total_frame, text="Total:", style='Header.TLabel').pack(side=tk.LEFT)
        self.total_label = ttk.Label(total_frame, text="0.00 Rs", style='Total.TLabel')
        self.total_label.pack(side=tk.RIGHT)

        # Control Buttons
        btn_frame = ttk.Frame(order_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(btn_frame, text="Checkout", command=self.process_checkout).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(btn_frame, text="Reset Order", command=self.reset_order).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Configure grid weights
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_columnconfigure(2, weight=1)
        main_frame.grid_columnconfigure(3, weight=0)
        main_frame.grid_rowconfigure(1, weight=1)

    def create_admin_button(self):
        admin_btn = ttk.Button(self.root, text="Admin Panel", style='Admin.TButton', command=self.show_admin_panel)
        admin_btn.place(relx=0.98, rely=0.02, anchor='ne')

    def create_menu_grid(self):
        menu_categories = {
            "Hot Beverages": [
                {'name': 'Coffee', 'price': 300},
                {'name': 'Cappuccino', 'price': 400},
                {'name': 'Latte', 'price': 400},
                {'name': 'Hot Chocolate', 'price': 400},
                {'name': 'Tea', 'price': 200},
                {'name': 'Espresso', 'price': 300},
            ],
            "Cold Beverages": [
                {'name': 'Iced Coffee', 'price': 400},
                {'name': 'Iced Latte', 'price': 400},
                {'name': 'Soda', 'price': 200},
                {'name': 'Fresh Juice', 'price': 400},
                {'name': 'Milkshake', 'price': 500},
                {'name': 'Smoothie', 'price': 500},
            ],
            "Breakfast": [
                {'name': 'Sandwich', 'price': 500},
                {'name': 'Croissant', 'price': 300},
                {'name': 'Pancakes', 'price': 600},
                {'name': 'Omelette', 'price': 600},
                {'name': 'Bagel', 'price': 400},
                {'name': 'French Toast', 'price': 700},
            ],
            "Lunch": [
                {'name': 'Salad', 'price': 700},
                {'name': 'Burger', 'price': 700},
                {'name': 'Pizza Slice', 'price': 500},
                {'name': 'Pasta', 'price': 800},
                {'name': 'Soup', 'price': 500},
                {'name': 'Wrap', 'price': 600},
            ],
            "Snacks": [
                {'name': 'Cake', 'price': 500},
                {'name': 'Muffin', 'price': 300},
                {'name': 'Cookies', 'price': 300},
                {'name': 'Donut', 'price': 300},
                {'name': 'Brownie', 'price': 400},
                {'name': 'Chips', 'price': 200},
            ]
        }

        menu_frame = self.root.pack_slaves()[0].grid_slaves(row=1, column=0)[0]
        
        # Create notebook for menu categories
        notebook = ttk.Notebook(menu_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        for category, items in menu_categories.items():
            tab = ttk.Frame(notebook)
            notebook.add(tab, text=category)
            
            for idx, item in enumerate(items):
                row = idx // 3
                col = idx % 3
                
                btn = ttk.Button(tab, text=f"{item['name']}\n{item['price']} Rs", 
                               style='Item.TButton',
                               command=lambda i=item: self.add_to_order(i))
                btn.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
                
                # Configure grid weights for even spacing
                tab.grid_columnconfigure(col, weight=1)
                tab.grid_rowconfigure(row, weight=1)

    def convert_to_email(self):
        roll_no = self.customer_id.get().strip()
        if roll_no.startswith('i') and roll_no[1:].isdigit():
            email = f"{roll_no}@isb.nu.edu.pk"
            self.customer_id.delete(0, tk.END)
            self.customer_id.insert(0, email)
        else:
            messagebox.showwarning("Format Error", "Roll number should be in format iXXXXXX")

    def add_to_order(self, item):
        name = item['name']
        if name in self.current_order:
            self.current_order[name]['quantity'] += 1
        else:
            self.current_order[name] = {'price': item['price'], 'quantity': 1}
        self.update_order_display()

    def update_order_display(self):
        self.order_text.delete(1.0, tk.END)
        total = 0
        
        # Add header
        self.order_text.insert(tk.END, "ITEM               QTY   PRICE   TOTAL\n")
        self.order_text.insert(tk.END, "-"*40 + "\n")
        
        # Add items
        for item, details in sorted(self.current_order.items()):
            item_total = details['price'] * details['quantity']
            line = f"{item[:18]:<18} {details['quantity']:^4} {details['price']:>5}Rs {item_total:>6}Rs\n"
            self.order_text.insert(tk.END, line)
            total += item_total
        
        # Add footer
        self.order_text.insert(tk.END, "-"*40 + "\n")
        self.total_label.config(text=f"{total} Rs")

    def check_customer(self):
        customer_id = self.customer_id.get().strip()
        if not customer_id:
            messagebox.showwarning("Input Error", "Please enter customer ID/Email")
            return
            
        # Convert roll no to email if needed
        if customer_id.startswith('i') and '@' not in customer_id and customer_id[1:].isdigit():
            customer_id = f"{customer_id}@isb.nu.edu.pk"

        if customer_id in self.users:
            transactions = self.users[customer_id]['transactions']
            msg = f"Customer: {customer_id}\nFirst seen: {self.users[customer_id]['first_seen']}\n\n"
            msg += "Last 3 transactions:\n"
            msg += "-"*40 + "\n"
            msg += "DATE/TIME           TOTAL\n"
            msg += "-"*40 + "\n"
            for t in transactions[-3:]:
                msg += f"{t['timestamp']}  {t['total']}Rs\n"
            msg += f"\nTotal visits: {len(transactions)}"
            messagebox.showinfo("Customer History", msg)
        else:
            messagebox.showinfo("Customer History", "New customer - no previous transactions")

    def process_checkout(self):
        customer_id = self.customer_id.get().strip()
        if not customer_id:
            messagebox.showerror("Error", "Please enter customer ID/Email")
            return
        if not self.current_order:
            messagebox.showerror("Error", "No items in order")
            return

        # Convert roll no to email if needed
        if customer_id.startswith('i') and '@' not in customer_id and customer_id[1:].isdigit():
            customer_id = f"{customer_id}@isb.nu.edu.pk"

        transaction = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'items': self.current_order,
            'total': float(self.total_label.cget('text').split('Rs')[0].strip())
        }

        if customer_id in self.users:
            self.users[customer_id]['transactions'].append(transaction)
        else:
            self.users[customer_id] = {
                'first_seen': datetime.now().strftime("%Y-%m-%d"),
                'transactions': [transaction]
            }

        self.save_users()
        receipt_text = self.generate_receipt_text(customer_id, transaction)
        self.show_receipt(customer_id, receipt_text)
        self.send_email_receipt(customer_id, receipt_text)
        self.reset_order()

    def generate_receipt_text(self, customer_id, transaction):
        receipt = f"""
        NATIONAL UNIVERSITY - ISLAMABAD CAMPUS
        {'='*45}
        Date: {transaction['timestamp']}
        Customer: {customer_id}
        {'-'*45}
        ITEM               QTY   PRICE   TOTAL
        {'-'*45}
        """
        
        for item, details in sorted(transaction['items'].items()):
            item_total = details['price'] * details['quantity']
            receipt += f"{item[:18]:<18} {details['quantity']:^4} {details['price']:>5}Rs {item_total:>6}Rs\n"
        
        receipt += f"{'-'*45}\n"
        receipt += f"{'TOTAL:':>38} {transaction['total']:>6.2f}Rs\n"
        receipt += f"{'='*45}\n"
        receipt += "Thank you for your purchase!\n"
        receipt += "       CafePOS Pro v1.0\n"
        return receipt

    def show_receipt(self, customer_id, receipt_text):
        messagebox.showinfo("Transaction Complete", receipt_text)
        self.print_to_file(customer_id, receipt_text)

    def send_email_receipt(self, customer_id, receipt_text):
        if not self.email_config.get("email") or not self.email_config.get("password"):
            messagebox.showwarning("Email Error", "Email configuration not set up properly")
            return

        try:
            msg = MIMEText(receipt_text)
            msg['Subject'] = f"Your Cafe Purchase Receipt - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            msg['From'] = self.email_config['email']
            msg['To'] = customer_id

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.email_config['email'], self.email_config['password'])
                server.sendmail(self.email_config['email'], [customer_id], msg.as_string())
                
            messagebox.showinfo("Email Sent", "Receipt has been sent to your email address")
        except Exception as e:
            messagebox.showerror("Email Error", f"Failed to send email: {str(e)}")

    def reset_order(self):
        self.current_order = {}
        self.update_order_display()

    def print_to_file(self, customer_id, receipt):
        os.makedirs("receipts", exist_ok=True)
        clean_id = customer_id.replace('@', '_at_')
        filename = f"receipts/{clean_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w') as f:
            f.write(receipt)

    def show_admin_panel(self):
        admin_window = tk.Toplevel(self.root)
        admin_window.title("Admin Panel")
        admin_window.geometry("1100x750")
        admin_window.resizable(True, True)

        # Create notebook for admin tabs
        notebook = ttk.Notebook(admin_window)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Dashboard Tab
        dashboard_tab = ttk.Frame(notebook)
        notebook.add(dashboard_tab, text="Dashboard")
        self.create_dashboard_tab(dashboard_tab)

        # User Management Tab
        user_tab = ttk.Frame(notebook)
        notebook.add(user_tab, text="User Management")

        # Section Header
        ttk.Label(user_tab, text="User Management", style='Header.TLabel').pack(anchor='w', padx=10, pady=(10,0))

        # Search and Actions Frame (grouped)
        top_frame = ttk.Frame(user_tab, padding=10)
        top_frame.pack(fill=tk.X)
        search_frame = ttk.Frame(top_frame)
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(search_frame, text="Search User:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Refresh", command=self.refresh_user_list).pack(side=tk.LEFT)
        action_frame = ttk.Frame(top_frame)
        action_frame.pack(side=tk.RIGHT)
        ttk.Button(action_frame, text="View Details", command=self.view_user_details).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Edit User", command=self.edit_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Delete User", command=self.delete_user).pack(side=tk.LEFT, padx=5)

        # User List Frame
        list_frame = ttk.Frame(user_tab)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Summary label
        self.user_summary_label = ttk.Label(list_frame, text=f"Total Users: {len(self.users)}", style='Subheader.TLabel')
        self.user_summary_label.pack(anchor='w', padx=5, pady=(0,5))

        # Treeview for users with striped rows
        self.user_tree = ttk.Treeview(list_frame, columns=('email', 'first_seen', 'transactions'), show='headings', selectmode='browse')
        self.user_tree.heading('email', text='Email/Roll No', command=lambda: self.sort_tree(self.user_tree, 'email', False))
        self.user_tree.heading('first_seen', text='First Seen', command=lambda: self.sort_tree(self.user_tree, 'first_seen', False))
        self.user_tree.heading('transactions', text='Transactions', command=lambda: self.sort_tree(self.user_tree, 'transactions', True))
        self.user_tree.column('email', width=250)
        self.user_tree.column('first_seen', width=100)
        self.user_tree.column('transactions', width=100)
        self.user_tree.tag_configure('oddrow', background='#f0f4f8')
        self.user_tree.tag_configure('evenrow', background='#ffffff')
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.user_tree.yview)
        hsb = ttk.Scrollbar(list_frame, orient="horizontal", command=self.user_tree.xview)
        self.user_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.user_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.user_tree.bind('<Double-1>', lambda e: self.view_user_details())
        self.refresh_user_list()

        # Transaction History Tab
        history_tab = ttk.Frame(notebook)
        notebook.add(history_tab, text="Transaction History")

        # Section Header
        ttk.Label(history_tab, text="Transaction History", style='Header.TLabel').pack(anchor='w', padx=10, pady=(10,0))

        # History Treeview
        self.history_tree = ttk.Treeview(history_tab, columns=('date', 'customer', 'items', 'total'), show='headings')
        self.history_tree.heading('date', text='Date/Time', command=lambda: self.sort_tree(self.history_tree, 'date', False))
        self.history_tree.heading('customer', text='Customer', command=lambda: self.sort_tree(self.history_tree, 'customer', False))
        self.history_tree.heading('items', text='Items')
        self.history_tree.heading('total', text='Total', command=lambda: self.sort_tree(self.history_tree, 'total', True))
        self.history_tree.column('date', width=150)
        self.history_tree.column('customer', width=200)
        self.history_tree.column('items', width=400)
        self.history_tree.column('total', width=100)

        vsb_history = ttk.Scrollbar(history_tab, orient="vertical", command=self.history_tree.yview)
        hsb_history = ttk.Scrollbar(history_tab, orient="horizontal", command=self.history_tree.xview)
        self.history_tree.configure(yscrollcommand=vsb_history.set, xscrollcommand=hsb_history.set)

        self.history_tree.pack(fill=tk.BOTH, expand=True)
        vsb_history.pack(side=tk.RIGHT, fill=tk.Y)
        hsb_history.pack(side=tk.BOTTOM, fill=tk.X)

        # Download CSV and Top Items Buttons
        btns_frame = ttk.Frame(history_tab)
        btns_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btns_frame, text="Download CSV", command=self.download_transactions_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns_frame, text="View Top Items", command=self.show_top_items_popup).pack(side=tk.LEFT, padx=5)

        # Load data
        self.refresh_user_list()
        self.load_transaction_history()

    def create_dashboard_tab(self, parent):
        # Visually appealing, interactive dashboard with responsive metric cards
        frame = ttk.Frame(parent, padding=30)
        frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frame, text="Admin Dashboard", style='Header.TLabel').pack(anchor='center', pady=(0,30))
        stats = self.get_dashboard_stats()
        cards_frame = tk.Frame(frame, bg='#f5f5f5')
        cards_frame.pack(anchor='center', pady=20, expand=True)
        # Card styles and icons (using emoji for simplicity)
        card_styles = [
            {'title': 'Total Users', 'value': stats['users'], 'color': '#3498db', 'icon': '👤'},
            {'title': 'Total Sales', 'value': f"{stats['sales']} Rs", 'color': '#27ae60', 'icon': '💰'},
            {'title': 'Total Transactions', 'value': stats['transactions'], 'color': '#e67e22', 'icon': '🧾'},
            {'title': 'Top Item', 'value': stats['top_item'], 'color': '#9b59b6', 'icon': '⭐'},
        ]
        card_widgets = []
        for i, card in enumerate(card_styles):
            card_frame = tk.Frame(cards_frame, bg=card['color'], bd=0, relief='ridge', cursor='hand2', highlightthickness=0)
            card_frame.grid(row=0, column=i, padx=25, ipadx=40, ipady=40, sticky='nsew')
            # Icon
            tk.Label(card_frame, text=card['icon'], font=('Arial', 38), fg='white', bg=card['color']).pack(pady=(0,5))
            # Title
            tk.Label(card_frame, text=card['title'], font=('Helvetica', 16, 'bold'), fg='white', bg=card['color']).pack()
            # Value
            tk.Label(card_frame, text=card['value'], font=('Helvetica', 26, 'bold'), fg='white', bg=card['color']).pack(pady=(10,0))
            # Shadow effect
            card_frame.config(highlightbackground='#888', highlightcolor='#888', highlightthickness=2)
            # Hover effect
            def on_enter(e, w=card_frame, c=card['color']):
                w.config(bg='#222222')
                for child in w.winfo_children():
                    child.config(bg='#222222')
            def on_leave(e, w=card_frame, c=card['color']):
                w.config(bg=c)
                for child in w.winfo_children():
                    child.config(bg=c)
            card_frame.bind('<Enter>', on_enter)
            card_frame.bind('<Leave>', on_leave)
            for widget in card_frame.winfo_children():
                widget.bind('<Enter>', on_enter)
                widget.bind('<Leave>', on_leave)
            card_frame.bind('<Button-1>', lambda e, idx=i: self.show_metric_details(idx))
            for widget in card_frame.winfo_children():
                widget.bind('<Button-1>', lambda e, idx=i: self.show_metric_details(idx))
            card_widgets.append(card_frame)
        # Responsive layout
        for i in range(len(card_styles)):
            cards_frame.grid_columnconfigure(i, weight=1)
        cards_frame.grid_rowconfigure(0, weight=1)

    def show_metric_details(self, idx):
        stats = self.get_dashboard_stats()
        popup = tk.Toplevel(self.root)
        popup.title("Metric Details")
        popup.geometry("500x500")
        popup.resizable(True, True)
        ttk.Label(popup, text="Metric Details", style='Header.TLabel').pack(pady=(10, 0))
        content_frame = ttk.Frame(popup, padding=15)
        content_frame.pack(fill=tk.BOTH, expand=True)
        if idx == 0:
            # Total Users detail
            ttk.Label(content_frame, text=f"Total Users: {stats['users']}", font=('Helvetica', 14, 'bold')).pack(anchor='w', pady=(0,10))
            tree = ttk.Treeview(content_frame, columns=("UserID",), show='headings', height=15)
            tree.heading("UserID", text="User ID / Email")
            for user in self.users.keys():
                tree.insert('', 'end', values=(user,))
            tree.pack(fill=tk.BOTH, expand=True)
        elif idx == 1:
            # Total Sales detail
            ttk.Label(content_frame, text=f"Total Sales: {stats['sales']} Rs", font=('Helvetica', 14, 'bold')).pack(anchor='w', pady=(0,10))
            tree = ttk.Treeview(content_frame, columns=("UserID", "Sales"), show='headings', height=15)
            tree.heading("UserID", text="User ID / Email")
            tree.heading("Sales", text="Total Sales (Rs)")
            for user, data in self.users.items():
                user_total = sum(t['total'] for t in data['transactions'])
                tree.insert('', 'end', values=(user, user_total))
            tree.pack(fill=tk.BOTH, expand=True)
        elif idx == 2:
            # Total Transactions detail
            ttk.Label(content_frame, text=f"Total Transactions: {stats['transactions']}", font=('Helvetica', 14, 'bold')).pack(anchor='w', pady=(0,10))
            tree = ttk.Treeview(content_frame, columns=("UserID", "Transactions"), show='headings', height=15)
            tree.heading("UserID", text="User ID / Email")
            tree.heading("Transactions", text="# Transactions")
            for user, data in self.users.items():
                tree.insert('', 'end', values=(user, len(data['transactions'])))
            tree.pack(fill=tk.BOTH, expand=True)
        else:
            # Top Item detail
            item_counter = {}
            for user in self.users.values():
                for t in user['transactions']:
                    for item, details in t['items'].items():
                        item_counter[item] = item_counter.get(item, 0) + details['quantity']
            sorted_items = sorted(item_counter.items(), key=lambda x: x[1], reverse=True)
            ttk.Label(content_frame, text="Top Sold Items", font=('Helvetica', 14, 'bold')).pack(anchor='w', pady=(0,10))
            tree = ttk.Treeview(content_frame, columns=("Item", "Quantity"), show='headings', height=15)
            tree.heading("Item", text="Item")
            tree.heading("Quantity", text="Quantity Sold")
            for item, qty in sorted_items[:10]:
                tree.insert('', 'end', values=(item, qty))
            tree.pack(fill=tk.BOTH, expand=True)
        ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)

    def get_dashboard_stats(self):
        total_users = len(self.users)
        total_sales = 0
        total_transactions = 0
        item_counter = {}
        for user in self.users.values():
            for t in user['transactions']:
                total_sales += t['total']
                total_transactions += 1
                for item, details in t['items'].items():
                    item_counter[item] = item_counter.get(item, 0) + details['quantity']
        top_item = max(item_counter, key=item_counter.get) if item_counter else 'N/A'
        return {
            'users': total_users,
            'sales': total_sales,
            'transactions': total_transactions,
            'top_item': top_item
        }

    def sort_tree(self, tree, col, numeric):
        # Sort treeview by column
        def parse_numeric(val):
            # Remove currency symbols and commas, then convert
            if isinstance(val, str):
                val = val.replace('$', '').replace('Rs', '').replace(',', '').strip()
            try:
                return float(val)
            except Exception:
                return 0
        data = [(tree.set(k, col), k) for k in tree.get_children('')]
        if numeric:
            data.sort(key=lambda t: parse_numeric(t[0]))
        else:
            data.sort()
        for index, (val, k) in enumerate(data):
            tree.move(k, '', index)

    def download_transactions_csv(self):
        file = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files', '*.csv')])
        if not file:
            return
        with open(file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Date/Time', 'Customer', 'Items', 'Total'])
            for row in self.history_tree.get_children():
                writer.writerow(self.history_tree.item(row)['values'])
        messagebox.showinfo("Export Complete", "Transactions exported as CSV.")

    def show_top_items_popup(self):
        # Show a popup with top sold items in a table format, with search, show all, sort, and export
        item_counter = {}
        for user in self.users.values():
            for t in user['transactions']:
                for item, details in t['items'].items():
                    item_counter[item] = item_counter.get(item, 0) + details['quantity']
        sorted_items = sorted(item_counter.items(), key=lambda x: x[1], reverse=True)
        show_all = {'value': False}
        filter_text = {'value': ''}
        popup = tk.Toplevel(self.root)
        popup.title("Top Sold Items")
        popup.geometry("400x400")
        popup.minsize(350, 250)
        popup.resizable(True, True)
        frame = ttk.Frame(popup, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frame, text="Top Sold Items", style='Header.TLabel').pack(anchor='center', pady=(0, 10))
        # Search bar
        search_frame = ttk.Frame(frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        search_entry = ttk.Entry(search_frame, width=25)
        search_entry.pack(side=tk.LEFT, padx=5)
        # Table
        columns = ("Item", "Quantity Sold")
        tree = ttk.Treeview(frame, columns=columns, show='headings', height=10)
        tree.heading("Item", text="Item", command=lambda: sort_table('Item', False))
        tree.heading("Quantity Sold", text="Quantity Sold", command=lambda: sort_table('Quantity Sold', True))
        tree.column("Item", width=180, anchor='w')
        tree.column("Quantity Sold", width=100, anchor='center')
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10), side=tk.LEFT)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        # Helper to populate table
        def populate_table():
            tree.delete(*tree.get_children())
            items = sorted_items if show_all['value'] else sorted_items[:5]
            if filter_text['value']:
                items = [x for x in items if filter_text['value'].lower() in x[0].lower()]
            for item, qty in items:
                tree.insert('', 'end', values=(item, qty))
        # Sorting
        def sort_table(col, numeric):
            data = [(tree.set(k, col), k) for k in tree.get_children('')]
            if numeric:
                data.sort(key=lambda t: float(t[0]) if t[0] else 0, reverse=True)
            else:
                data.sort(reverse=False)
            for index, (val, k) in enumerate(data):
                tree.move(k, '', index)
        # Search event
        def on_search(*args):
            filter_text['value'] = search_entry.get()
            populate_table()
        search_entry.bind('<KeyRelease>', on_search)
        # Show All button
        def toggle_show_all():
            show_all['value'] = not show_all['value']
            show_btn.config(text="Show Top 5" if show_all['value'] else "Show All")
            populate_table()
        show_btn = ttk.Button(frame, text="Show All", command=toggle_show_all)
        show_btn.pack(side=tk.LEFT, pady=5, padx=(0, 5), anchor='w')
        # Export as CSV
        def export_csv():
            file = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files', '*.csv')], title='Export Top Items')
            if not file:
                return
            items = sorted_items if show_all['value'] else sorted_items[:5]
            if filter_text['value']:
                items = [x for x in items if filter_text['value'].lower() in x[0].lower()]
            with open(file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Item', 'Quantity Sold'])
                for item, qty in items:
                    writer.writerow([item, qty])
            messagebox.showinfo("Export Complete", "Top items exported as CSV.")
        export_btn = ttk.Button(frame, text="Export as CSV", command=export_csv)
        export_btn.pack(side=tk.LEFT, pady=5, padx=(0, 5), anchor='w')
        # Close button
        ttk.Button(frame, text="Close", command=popup.destroy).pack(side=tk.RIGHT, pady=5, anchor='e')
        populate_table()

    def search_user(self):
        query = self.search_entry.get().lower()
        self.user_tree.delete(*self.user_tree.get_children())
        
        for user_id, data in self.users.items():
            if query in user_id.lower():
                self.user_tree.insert('', 'end', values=(
                    user_id,
                    data['first_seen'],
                    len(data['transactions'])
                ))

    def refresh_user_list(self):
        self.user_tree.delete(*self.user_tree.get_children())
        for idx, (user_id, data) in enumerate(self.users.items()):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.user_tree.insert('', 'end', values=(
                user_id,
                data['first_seen'],
                len(data['transactions'])
            ), tags=(tag,))
        if hasattr(self, 'user_summary_label'):
            self.user_summary_label.config(text=f"Total Users: {len(self.users)}")

    def load_transaction_history(self):
        self.history_tree.delete(*self.history_tree.get_children())
        for user_id, data in self.users.items():
            for transaction in data['transactions']:
                items = ", ".join([f"{item} x{details['quantity']}" for item, details in transaction['items'].items()])
                self.history_tree.insert('', 'end', values=(
                    transaction['timestamp'],
                    user_id,
                    items,
                    f"${transaction['total']:.2f}"
                ))

    def view_user_details(self):
        selected = self.user_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a user first")
            return
        user_id = self.user_tree.item(selected[0])['values'][0]
        user_data = self.users[user_id]
        details_window = tk.Toplevel(self.root)
        details_window.title(f"User Details - {user_id}")
        details_window.geometry("800x550")
        details_window.minsize(600, 350)
        details_window.resizable(True, True)
        main_frame = ttk.Frame(details_window, padding=20)
        main_frame.grid(row=0, column=0, sticky='nsew')
        details_window.grid_rowconfigure(0, weight=1)
        details_window.grid_columnconfigure(0, weight=1)
        # User Info Section
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        info_frame.grid_columnconfigure(0, weight=1)
        ttk.Label(info_frame, text=f"User ID: {user_id}", font=('Helvetica', 13, 'bold')).grid(row=0, column=0, sticky='w')
        ttk.Label(info_frame, text=f"First Seen: {user_data['first_seen']}", font=('Helvetica', 11)).grid(row=1, column=0, sticky='w')
        ttk.Label(info_frame, text=f"Total Transactions: {len(user_data['transactions'])}", font=('Helvetica', 11)).grid(row=2, column=0, sticky='w')
        # Export Button
        export_btn = ttk.Button(info_frame, text="Export Transactions", command=lambda: self.export_user_transactions(user_id))
        export_btn.grid(row=0, column=1, rowspan=3, padx=10, sticky='e')
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=1, column=0, sticky='ew', pady=5)
        # Search Bar
        search_frame = ttk.Frame(main_frame)
        search_frame.grid(row=2, column=0, sticky='ew', pady=(0, 5))
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        search_entry = ttk.Entry(search_frame, width=40)
        search_entry.pack(side=tk.LEFT, padx=5)
        # Transactions Section
        table_frame = ttk.Frame(main_frame)
        table_frame.grid(row=3, column=0, sticky='nsew')
        main_frame.grid_rowconfigure(3, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        columns = ("Date", "Total", "Items")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        tree.heading("Date", text="Date/Time", command=lambda: self.sort_user_transactions(tree, 0, False))
        tree.heading("Total", text="Total (Rs)", command=lambda: self.sort_user_transactions(tree, 1, True))
        tree.heading("Items", text="Items")
        tree.column("Date", width=150, anchor='center')
        tree.column("Total", width=100, anchor='center')
        tree.column("Items", width=400, anchor='w')
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        # Populate transactions
        def populate_tree(filter_text=None):
            tree.delete(*tree.get_children())
            for trans in user_data['transactions']:
                items = ", ".join([f"{item} x{details['quantity']}" for item, details in trans['items'].items()])
                if filter_text:
                    if (filter_text.lower() not in trans['timestamp'].lower() and
                        filter_text.lower() not in items.lower() and
                        filter_text.lower() not in str(trans['total'])):
                        continue
                tree.insert('', 'end', values=(trans['timestamp'], f"{trans['total']:.2f}", items))
        populate_tree()
        def on_search(*args):
            populate_tree(search_entry.get())
        search_entry.bind('<KeyRelease>', on_search)
        # Responsive resizing
        details_window.grid_rowconfigure(0, weight=1)
        details_window.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(3, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        # Close Button
        ttk.Button(main_frame, text="Close", command=details_window.destroy).grid(row=4, column=0, pady=10, sticky='e')

    def export_user_transactions(self, user_id):
        user_data = self.users[user_id]
        file = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files', '*.csv')], title='Export User Transactions')
        if not file:
            return
        with open(file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Date/Time', 'Total (Rs)', 'Items'])
            for trans in user_data['transactions']:
                items = ", ".join([f"{item} x{details['quantity']}" for item, details in trans['items'].items()])
                writer.writerow([trans['timestamp'], f"{trans['total']:.2f}", items])
        messagebox.showinfo("Export Complete", f"Transactions for {user_id} exported as CSV.")

    def sort_user_transactions(self, tree, col_idx, numeric):
        data = [(tree.set(k, tree['columns'][col_idx]), k) for k in tree.get_children('')]
        if numeric:
            data.sort(key=lambda t: float(t[0]) if t[0] else 0)
        else:
            data.sort()
        for index, (val, k) in enumerate(data):
            tree.move(k, '', index)

    def edit_user(self):
        selected = self.user_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a user first")
            return
            
        old_id = self.user_tree.item(selected[0])['values'][0]
        user_data = self.users[old_id]
        
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Edit User - {old_id}")
        edit_window.geometry("400x200")
        
        ttk.Label(edit_window, text="New User ID/Email:").pack(pady=5)
        new_id_entry = ttk.Entry(edit_window, width=40)
        new_id_entry.insert(0, old_id)
        new_id_entry.pack(pady=5)
        
        def save_changes():
            new_id = new_id_entry.get().strip()
            if not new_id:
                messagebox.showerror("Error", "User ID cannot be empty")
                return
                
            if new_id != old_id:
                if new_id in self.users:
                    messagebox.showerror("Error", "User ID already exists")
                    return
                    
                self.users[new_id] = self.users.pop(old_id)
                self.save_users()
                self.refresh_user_list()
                messagebox.showinfo("Success", "User updated successfully")
                edit_window.destroy()
            else:
                messagebox.showinfo("Info", "No changes made")
                edit_window.destroy()
        
        ttk.Button(edit_window, text="Save Changes", command=save_changes).pack(pady=10)

    def delete_user(self):
        selected = self.user_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a user first")
            return
        user_id = self.user_tree.item(selected[0])['values'][0]
        # Store for undo
        deleted_user = {'id': user_id, 'data': self.users[user_id]}
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user {user_id}?"):
            del self.users[user_id]
            self.save_users()
            self.refresh_user_list()
            # Show undo option
            undo_popup = tk.Toplevel(self.root)
            undo_popup.title("Undo Delete")
            undo_popup.geometry("300x100")
            ttk.Label(undo_popup, text=f"User {user_id} deleted.").pack(pady=10)
            def undo():
                self.users[deleted_user['id']] = deleted_user['data']
                self.save_users()
                self.refresh_user_list()
                undo_popup.destroy()
                messagebox.showinfo("Undo", f"User {user_id} restored.")
            ttk.Button(undo_popup, text="Undo", command=undo).pack(pady=5)
            # Auto-close after 5 seconds
            def close_after_delay():
                undo_popup.after(5000, lambda: undo_popup.destroy())
            threading.Thread(target=close_after_delay, daemon=True).start()
            messagebox.showinfo("Success", "User deleted successfully")

if __name__ == "__main__":
    root = tk.Tk()
    app = CafeteriaPOS(root)
    root.mainloop()