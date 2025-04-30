import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import json
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

class CafeteriaPOS:
    def __init__(self, root):
        self.root = root
        self.root.title("CafePOS Pro - NU Islamabad")
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
                       font=('Arial', 34, 'bold'),  # Increased from 14 to 16
                       width=22, 
                       padding=18,  # Increased from 10 to 12
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

        ttk.Label(customer_frame, text="Fast NU Islamabad POS System", style='Header.TLabel').grid(row=0, column=0, columnspan=4, sticky='w')
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
        admin_window.geometry("1000x700")
        admin_window.resizable(True, True)

        # Create notebook for admin tabs
        notebook = ttk.Notebook(admin_window)
        notebook.pack(fill=tk.BOTH, expand=True)

        # User Management Tab
        user_tab = ttk.Frame(notebook)
        notebook.add(user_tab, text="User Management")

        # Search Frame
        search_frame = ttk.Frame(user_tab, padding=10)
        search_frame.pack(fill=tk.X)

        ttk.Label(search_frame, text="Search User:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Refresh", command=self.refresh_user_list).pack(side=tk.LEFT)

        # User List Frame
        list_frame = ttk.Frame(user_tab)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Treeview for users
        self.user_tree = ttk.Treeview(list_frame, columns=('email', 'first_seen', 'transactions'), show='headings')
        self.user_tree.heading('email', text='Email/Roll No')
        self.user_tree.heading('first_seen', text='First Seen')
        self.user_tree.heading('transactions', text='Transactions')
        self.user_tree.column('email', width=250)
        self.user_tree.column('first_seen', width=100)
        self.user_tree.column('transactions', width=100)

        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.user_tree.yview)
        hsb = ttk.Scrollbar(list_frame, orient="horizontal", command=self.user_tree.xview)
        self.user_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.user_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        # Action Buttons
        action_frame = ttk.Frame(user_tab)
        action_frame.pack(fill=tk.X, pady=5)

        ttk.Button(action_frame, text="View Details", command=self.view_user_details).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Edit User", command=self.edit_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Delete User", command=self.delete_user).pack(side=tk.LEFT, padx=5)

        # Transaction History Tab
        history_tab = ttk.Frame(notebook)
        notebook.add(history_tab, text="Transaction History")

        # History Treeview
        self.history_tree = ttk.Treeview(history_tab, columns=('date', 'customer', 'items', 'total'), show='headings')
        self.history_tree.heading('date', text='Date/Time')
        self.history_tree.heading('customer', text='Customer')
        self.history_tree.heading('items', text='Items')
        self.history_tree.heading('total', text='Total')
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

        # Load data
        self.refresh_user_list()
        self.load_transaction_history()

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
        for user_id, data in self.users.items():
            self.user_tree.insert('', 'end', values=(
                user_id,
                data['first_seen'],
                len(data['transactions'])
            ))

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
        details_window.geometry("600x400")
        
        # Create notebook for details
        notebook = ttk.Notebook(details_window)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Info Tab
        info_tab = ttk.Frame(notebook)
        notebook.add(info_tab, text="User Info")
        
        ttk.Label(info_tab, text=f"User ID: {user_id}").pack(anchor='w', pady=5)
        ttk.Label(info_tab, text=f"First Seen: {user_data['first_seen']}").pack(anchor='w', pady=5)
        ttk.Label(info_tab, text=f"Total Transactions: {len(user_data['transactions'])}").pack(anchor='w', pady=5)
        
        # Transactions Tab
        trans_tab = ttk.Frame(notebook)
        notebook.add(trans_tab, text="Transactions")
        
        trans_text = scrolledtext.ScrolledText(trans_tab, wrap=tk.WORD)
        trans_text.pack(fill=tk.BOTH, expand=True)
        
        for trans in user_data['transactions']:
            trans_text.insert(tk.END, f"Date: {trans['timestamp']}\n")
            trans_text.insert(tk.END, f"Total: ${trans['total']:.2f}\n")
            trans_text.insert(tk.END, "Items:\n")
            for item, details in trans['items'].items():
                trans_text.insert(tk.END, f"  - {item} x{details['quantity']} @ ${details['price']:.2f}\n")
            trans_text.insert(tk.END, "-"*40 + "\n")

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
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user {user_id}?"):
            del self.users[user_id]
            self.save_users()
            self.refresh_user_list()
            messagebox.showinfo("Success", "User deleted successfully")

if __name__ == "__main__":
    root = tk.Tk()
    app = CafeteriaPOS(root)
    root.mainloop()