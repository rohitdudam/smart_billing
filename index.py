import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import speech_recognition as sr
import pyttsx3
import sqlite3
from datetime import datetime
import threading

# Set modern appearance
ctk.set_appearance_mode("Light") 
ctk.set_default_color_theme("blue") 

class NexusPro:
    def __init__(self, root):
        self.root = root
        self.root.title("Rajendra Gruh Vastu Bhandar - Modern POS")
        self.root.geometry("1300x850")
        
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 160)
        self.init_db()
        
        self.session_customer = {"name": "Walk-in", "phone": "N/A"}
        self.cart = [] 
        self.editing_item_idx = None 
        self.editing_row_id = None

        self.setup_styles()
        self.create_layout()
        self.show_login_overlay() 

    def init_db(self):
        self.conn = sqlite3.connect("rajendra_gruh_vastu.db")
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY, name TEXT UNIQUE, p_rate REAL, s_rate REAL, stock INTEGER)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY, name TEXT, phone TEXT UNIQUE)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS sales (id INTEGER PRIMARY KEY, customer TEXT, item TEXT, qty INTEGER, total REAL, profit REAL, date TEXT)")
        self.conn.commit()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=40, font=("Segoe UI", 11), background="#ffffff", fieldbackground="#ffffff", borderwidth=0)
        style.configure("Treeview.Heading", background="#0a3d62", foreground="white", font=("Segoe UI", 11, "bold"), borderwidth=0)
        style.map("Treeview", background=[("selected", "#e1f0fa")], foreground=[("selected", "#0a3d62")])

    def create_layout(self):
        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self.root, width=250, corner_radius=0, fg_color="#0a3d62")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(self.sidebar, text="Rajendra GVB", font=("Segoe UI Black", 22), text_color="white", pady=30).pack()

        menus = [
            ("📁 Dashboard", self.show_reports),
            ("📝 BILLING", self.ui_billing),
            ("📦 INVENTORY", self.ui_inventory),
            ("📊 PROFIT & LOSS", self.show_reports),
            ("👥 CUSTOMERS", self.ui_customers),
            ("⚙️ SETTINGS", lambda: messagebox.showinfo("Info", "Settings optimized."))
        ]

        self.nav_btns = []
        for text, cmd in menus:
            btn = ctk.CTkButton(self.sidebar, text=text, font=("Segoe UI", 13, "bold"), fg_color="transparent", 
                                text_color="white", hover_color="#145c91", anchor="w", height=45, command=cmd)
            btn.pack(fill="x", padx=10, pady=5)
            self.nav_btns.append((text, btn))

        # --- Main Content ---
        self.content = ctk.CTkFrame(self.root, corner_radius=0, fg_color="#f1f2f6")
        self.content.pack(side="right", fill="both", expand=True)

    def clear_content(self):
        for widget in self.content.winfo_children(): widget.destroy()

    def set_active_nav(self, active_text):
        for text, btn in self.nav_btns:
            btn.configure(fg_color="#145c91" if text == active_text else "transparent")

    # --- TAB 1: POS BILLING ---
    def ui_billing(self):
        self.clear_content()
        self.set_active_nav("📝 BILLING")
        
        # Header
        header = ctk.CTkFrame(self.content, fg_color="transparent", height=50)
        header.pack(fill="x", padx=20, pady=(15, 5))
        ctk.CTkLabel(header, text="Point of Sale", font=("Segoe UI", 24, "bold"), text_color="#0a3d62").pack(side="left")
        ctk.CTkLabel(header, text=f"👤 Cashier: Rajendra", font=("Segoe UI", 13, "bold"), text_color="#2c3e50").pack(side="right", padx=10)

        # Voice Status Banner
        self.voice_status_bar = ctk.CTkLabel(self.content, text="", font=("Segoe UI", 12, "bold"), fg_color="transparent", text_color="#f1f2f6", corner_radius=8, height=30)
        self.voice_status_bar.pack(fill="x", padx=20)

        # Search & Mic
        search_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=5)
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="🔍 Search Items or Scan Barcode...", height=45, font=("Arial", 14), corner_radius=8, fg_color="white", border_color="#d1d8e0")
        self.search_entry.pack(side="left", fill="both", expand=True)
        self.mic_btn = ctk.CTkButton(search_frame, text="🎤", font=("Segoe UI", 20), width=60, height=45, fg_color="#0a3d62", hover_color="#2ecc71", corner_radius=8, command=self.process_voice)
        self.mic_btn.pack(side="left", padx=(10, 0))

        # Main Cards Area
        cards_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        cards_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # --- LEFT: TRANSACTION CARD ---
        trans_card = ctk.CTkFrame(cards_frame, corner_radius=12, fg_color="white", border_width=1, border_color="#e1e8ed")
        trans_card.pack(side="left", fill="both", expand=True, padx=(0, 15))

        # Manual Entry (Modernized - Fixed Padding logic)
        m_frame = ctk.CTkFrame(trans_card, fg_color="#f8f9fa", corner_radius=8)
        m_frame.pack(fill="x", padx=15, pady=(15, 5))
        
        # Inner frame to organize the inputs neatly
        m_inner = tk.Frame(m_frame, bg="#f8f9fa")
        m_inner.pack(padx=15, pady=15)
        
        ctk.CTkLabel(m_inner, text="Item:", font=("Segoe UI", 12, "bold"), text_color="#2c3e50").pack(side="left", padx=(5, 5))
        self.b_item = ctk.CTkEntry(m_inner, width=160, font=("Arial", 12), height=35, fg_color="white", border_width=1)
        self.b_item.pack(side="left", padx=(0, 15))
        
        ctk.CTkLabel(m_inner, text="Qty:", font=("Segoe UI", 12, "bold"), text_color="#2c3e50").pack(side="left", padx=(0, 5))
        self.b_qty = ctk.CTkEntry(m_inner, width=70, font=("Arial", 12), height=35, fg_color="white", border_width=1)
        self.b_qty.pack(side="left", padx=(0, 15))
        
        ctk.CTkLabel(m_inner, text="Rate:", font=("Segoe UI", 12, "bold"), text_color="#2c3e50").pack(side="left", padx=(0, 5))
        self.b_rate = ctk.CTkEntry(m_inner, width=90, font=("Arial", 12), height=35, fg_color="white", border_width=1)
        self.b_rate.pack(side="left", padx=(0, 15))
        self.b_rate.bind("<Return>", lambda e: self.add_or_update_bill_manual())

        self.btn_manual = ctk.CTkButton(m_inner, text="➕ Add", font=("Segoe UI", 12, "bold"), width=80, height=35, fg_color="#0a3d62", command=self.add_or_update_bill_manual)
        self.btn_manual.pack(side="left", padx=10)

        # Treeview Table
        tree_frame = tk.Frame(trans_card, bg="white")
        tree_frame.pack(fill="both", expand=True, padx=15, pady=5)
        
        cols = ("Item Name", "Qty", "Price", "Total", "Edit", "Remove")
        self.bill_tree = ttk.Treeview(tree_frame, columns=cols, show='headings', selectmode="browse")
        for i, col in enumerate(cols):
            anchor, w = ("w", 200) if i == 0 else ("center", 80)
            self.bill_tree.heading(col, text=col, anchor=anchor)
            self.bill_tree.column(col, anchor=anchor, width=w)
        self.bill_tree.pack(fill="both", expand=True)
        self.bill_tree.bind("<Button-1>", self.table_click_logic)

        # Footer Total
        total_frame = ctk.CTkFrame(trans_card, fg_color="#3c6382", corner_radius=0, height=60)
        total_frame.pack(fill="x", side="bottom")
        self.lbl_total = ctk.CTkLabel(total_frame, text="GRAND TOTAL: $0.00", font=("Segoe UI", 20, "bold"), text_color="white")
        self.lbl_total.pack(side="left", padx=20, pady=15)
        ctk.CTkButton(total_frame, text="CHECKOUT ➤", font=("Segoe UI", 13, "bold"), fg_color="#27ae60", hover_color="#2ecc71", command=self.checkout).pack(side="right", padx=20)

        # --- RIGHT PANEL ---
        right_panel = ctk.CTkFrame(cards_frame, fg_color="transparent", width=320)
        right_panel.pack(side="right", fill="y")
        right_panel.pack_propagate(False)

        # Customer Card
        cust_card = ctk.CTkFrame(right_panel, fg_color="white", corner_radius=12, border_width=1, border_color="#e1e8ed")
        cust_card.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(cust_card, text="Active Customer", font=("Segoe UI", 14, "bold"), text_color="#0a3d62").pack(anchor="w", padx=15, pady=(10, 0))
        ctk.CTkLabel(cust_card, text=f"👤 {self.session_customer['name']}\n📞 {self.session_customer['phone']}", font=("Segoe UI", 14), text_color="#2c3e50", justify="left").pack(anchor="w", padx=15, pady=10)

        # Calculator Card
        calc_card = ctk.CTkFrame(right_panel, fg_color="white", corner_radius=12, border_width=1, border_color="#e1e8ed")
        calc_card.pack(fill="both", expand=True)
        ctk.CTkLabel(calc_card, text="Calculator", font=("Segoe UI", 14, "bold"), text_color="#0a3d62").pack(anchor="w", padx=15, pady=(10, 5))
        
        self.calc_disp = ctk.CTkEntry(calc_card, font=("Arial", 22, "bold"), height=50, justify="right", fg_color="#f1f2f6", border_width=0)
        self.calc_disp.pack(fill="x", padx=15, pady=(0, 10))

        c_grid = ctk.CTkFrame(calc_card, fg_color="transparent")
        c_grid.pack(fill="both", expand=True, padx=10, pady=10)

        buttons = [('7',0,0), ('8',0,1), ('9',0,2), ('/',0,3), ('4',1,0), ('5',1,1), ('6',1,2), ('*',1,3), ('1',2,0), ('2',2,1), ('3',2,2), ('-',2,3), ('C',3,0), ('0',3,1), ('=',3,2), ('+',3,3)]
        for (txt, r, c) in buttons:
            color = "#2ecc71" if txt == "=" else "#e74c3c" if txt == "C" else "#f1f2f6"
            txt_color = "white" if txt in ["=", "C"] else "#2c3e50"
            cmd = self.calc_eval if txt == "=" else self.calc_clear if txt == "C" else lambda t=txt: self.calc_click(t)
            btn = ctk.CTkButton(c_grid, text=txt, font=("Segoe UI", 16, "bold"), fg_color=color, text_color=txt_color, hover_color="#d1d8e0" if txt not in ["=","C"] else color, command=cmd)
            btn.grid(row=r, column=c, sticky="nsew", padx=4, pady=4)
        for i in range(4): c_grid.grid_columnconfigure(i, weight=1); c_grid.grid_rowconfigure(i, weight=1)

    # --- CALCULATOR LOGIC ---
    def calc_click(self, char):
        curr = self.calc_disp.get()
        if curr == "Error": curr = ""
        self.calc_disp.delete(0, tk.END); self.calc_disp.insert(0, str(curr) + str(char))
    def calc_clear(self): self.calc_disp.delete(0, tk.END)
    def calc_eval(self):
        try:
            res = eval(self.calc_disp.get())
            self.calc_disp.delete(0, tk.END); self.calc_disp.insert(0, f"{res:.2f}" if isinstance(res, float) else str(res))
        except: self.calc_disp.delete(0, tk.END); self.calc_disp.insert(0, "Error")

    # --- BILLING LOGIC ---
    def process_cart_entry(self, name, qty, rate):
        try:
            q, r = int(qty), float(rate)
            tot = q * r
            self.cur.execute("SELECT p_rate FROM inventory WHERE name=?", (name.lower(),))
            p_res = self.cur.fetchone()
            prof = (r - (p_res[0] if p_res else 0.0)) * q
            
            self.cart.append({"name": name, "qty": q, "rate": r, "total": tot, "profit": prof})
            c_idx = len(self.cart) - 1
            self.bill_tree.insert("", "end", values=(name.capitalize(), q, f"${r:.2f}", f"${tot:.2f}", "✏️", "🗑️"), tags=(f"cart_{c_idx}",))
            
            self.lbl_total.configure(text=f"GRAND TOTAL: ${sum(i['total'] for i in self.cart):.2f}")
            self.speak(f"Added {name}")
        except: messagebox.showerror("Error", "Invalid Numeric Data")

    def add_or_update_bill_manual(self):
        n, q, r = self.b_item.get(), self.b_qty.get(), self.b_rate.get()
        if n and q and r:
            if self.editing_row_id:
                try:
                    q_int, r_flt = int(q), float(r)
                    tot = q_int * r_flt
                    self.cart[self.editing_item_idx].update({"name": n, "qty": q_int, "rate": r_flt, "total": tot})
                    self.bill_tree.item(self.editing_row_id, values=(n.capitalize(), q_int, f"${r_flt:.2f}", f"${tot:.2f}", "✏️", "🗑️"))
                    self.lbl_total.configure(text=f"GRAND TOTAL: ${sum(i['total'] for i in self.cart):.2f}")
                    self.editing_row_id = None; self.btn_manual.configure(text="➕ Add", fg_color="#0a3d62")
                except: messagebox.showerror("Error", "Invalid update format")
            else:
                self.process_cart_entry(n, q, r)
            self.b_item.delete(0, 'end'); self.b_qty.delete(0, 'end'); self.b_rate.delete(0, 'end'); self.b_item.focus_set()

    def table_click_logic(self, e):
        row = self.bill_tree.identify_row(e.y)
        col = self.bill_tree.identify_column(e.x)
        if not row: return
        try: idx = int([t for t in self.bill_tree.item(row, 'tags') if t.startswith("cart_")][0][5:])
        except: return
        
        if col == "#5": # Edit
            itm = self.cart[idx]
            self.b_item.delete(0, 'end'); self.b_item.insert(0, itm['name'])
            self.b_qty.delete(0, 'end'); self.b_qty.insert(0, itm['qty'])
            self.b_rate.delete(0, 'end'); self.b_rate.insert(0, itm['rate'])
            self.editing_item_idx, self.editing_row_id = idx, row
            self.btn_manual.configure(text="🔄 Update", fg_color="#f39c12")
        elif col == "#6": # Remove
            if messagebox.askyesno("Remove", "Remove item?"):
                del self.cart[idx]; self.bill_tree.delete(row)
                self.lbl_total.configure(text=f"GRAND TOTAL: ${sum(i['total'] for i in self.cart):.2f}")

    def checkout(self):
        if not self.cart: return
        dt = datetime.now().strftime("%Y-%m-%d %H:%M")
        for i in self.cart:
            self.cur.execute("INSERT INTO sales (customer, item, qty, total, profit, date) VALUES (?,?,?,?,?,?)",
                             (self.session_customer['name'], i['name'], i['qty'], i['total'], i.get('profit', 0), dt))
        self.conn.commit(); self.cart = []; self.ui_billing()
        self.update_voice_banner("✅ Checkout Successful!", "#2ecc71")

    # --- VOICE CONTROL (Threaded) ---
    def process_voice(self):
        self.mic_btn.configure(fg_color="#e74c3c") 
        self.update_voice_banner("🎙️ Listening... (Speak clearly)", "#3498db")
        threading.Thread(target=self._voice_worker, daemon=True).start()

    def _voice_worker(self):
        r = sr.Recognizer(); r.pause_threshold = 0.8 
        with sr.Microphone() as src:
            r.adjust_for_ambient_noise(src, duration=0.4) 
            try:
                aud = r.listen(src, timeout=5, phrase_time_limit=5) 
                self.root.after(0, self.update_voice_banner, "⚙️ Processing...", "#f39c12")
                txt = r.recognize_google(aud).lower()
                words = txt.split()
                if "add" in words:
                    i = words.index("add")
                    itm = words[i+1]
                    q = words[words.index("quantity")+1] if "quantity" in words else words[2] if len(words)>3 else "1"
                    rt = words[words.index("rate")+1] if "rate" in words else words[3] if len(words)>3 else "0"
                    self.root.after(0, self.process_cart_entry, itm, q, rt)
                    self.root.after(0, self.update_voice_banner, f"✅ Added: {txt.capitalize()}", "#2ecc71")
                else: self.root.after(0, self.update_voice_banner, "⚠️ Say 'Add [Item] [Qty] [Rate]'", "#e74c3c")
            except sr.WaitTimeoutError: self.root.after(0, self.update_voice_banner, "⚠️ Timed out", "#e74c3c")
            except sr.UnknownValueError: self.root.after(0, self.update_voice_banner, "⚠️ Didn't catch that", "#e74c3c")
            except Exception as e: print(e)
            finally:
                self.root.after(0, self.mic_btn.configure, {"fg_color": "#0a3d62"})
                self.root.after(3000, self.clear_voice_banner)

    def update_voice_banner(self, txt, col):
        if hasattr(self, 'voice_status_bar') and self.voice_status_bar.winfo_exists():
            self.voice_status_bar.configure(text=txt, fg_color=col)
            
    def clear_voice_banner(self): self.update_voice_banner("", "transparent")

    # --- INVENTORY & OTHERS (Fully Restored & Modernized) ---
    def show_reports(self):
        self.clear_content()
        self.set_active_nav("📊 PROFIT & LOSS")
        ctk.CTkLabel(self.content, text="Financial Dashboard", font=("Segoe UI", 24, "bold"), text_color="#0a3d62").pack(pady=30)
        self.cur.execute("SELECT SUM(profit) FROM sales")
        card = ctk.CTkFrame(self.content, fg_color="white", corner_radius=15)
        card.pack(pady=20)
        ctk.CTkLabel(card, text="Total Net Profit", font=("Segoe UI", 16), text_color="#7f8c8d").pack(pady=(40, 0), padx=80)
        ctk.CTkLabel(card, text=f"${(self.cur.fetchone()[0] or 0.0):,.2f}", font=("Arial", 60, "bold"), text_color="#2ecc71").pack(pady=(10, 40), padx=80)

    def ui_inventory(self):
        self.clear_content()
        self.set_active_nav("📦 INVENTORY")
        ctk.CTkLabel(self.content, text="Inventory Bulk Manager", font=("Segoe UI", 24, "bold"), text_color="#0a3d62").pack(pady=20)

        # Wrap standard frame inside CTkFrame for strict padding rules
        form_wrapper = ctk.CTkFrame(self.content, fg_color="white", corner_radius=10)
        form_wrapper.pack(pady=10, padx=30, fill="x")
        
        form = tk.Frame(form_wrapper, bg="white")
        form.pack(padx=20, pady=20, fill="x")
        
        self.inv_entries = []
        labels = ["Item Name", "Cost (P-Rate)", "Price (S-Rate)", "Stock"]
        for i, text in enumerate(labels):
            tk.Label(form, text=text, bg="white", font=("Segoe UI", 10, "bold"), fg="#2c3e50").grid(row=0, column=i*2)
            e = ctk.CTkEntry(form, width=130, font=("Arial", 12), height=35)
            e.grid(row=0, column=i*2+1, padx=10)
            self.inv_entries.append(e)

        ctk.CTkButton(form, text="Save Item", fg_color="#0a3d62", font=("Segoe UI", 12, "bold"), width=100, height=35, command=self.save_to_inventory).grid(row=0, column=8, padx=10)

        tree_frame = tk.Frame(self.content, bg="white")
        tree_frame.pack(pady=20, padx=30, fill="both", expand=True)

        self.inv_tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "Cost", "Price", "Stock"), show='headings')
        for col in ("ID", "Name", "Cost", "Price", "Stock"): self.inv_tree.heading(col, text=col)
        self.inv_tree.pack(fill="both", expand=True)
        self.refresh_inventory()

    def ui_customers(self):
        self.clear_content()
        self.set_active_nav("👥 CUSTOMERS")
        ctk.CTkLabel(self.content, text="Customer Registry", font=("Segoe UI", 24, "bold"), text_color="#0a3d62").pack(pady=20)

        c_wrapper = ctk.CTkFrame(self.content, fg_color="white", corner_radius=10)
        c_wrapper.pack(pady=10, padx=30, fill="x")
        
        c_form = tk.Frame(c_wrapper, bg="white")
        c_form.pack(padx=20, pady=20, fill="x")
        
        tk.Label(c_form, text="Full Name:", bg="white", font=("Segoe UI", 10, "bold"), fg="#2c3e50").grid(row=0, column=0)
        self.reg_name = ctk.CTkEntry(c_form, width=200, font=("Arial", 12), height=35)
        self.reg_name.grid(row=0, column=1, padx=10)
        
        tk.Label(c_form, text="Phone:", bg="white", font=("Segoe UI", 10, "bold"), fg="#2c3e50").grid(row=0, column=2)
        self.reg_phone = ctk.CTkEntry(c_form, width=150, font=("Arial", 12), height=35)
        self.reg_phone.grid(row=0, column=3, padx=10)
        
        ctk.CTkButton(c_form, text="Register", fg_color="#0a3d62", font=("Segoe UI", 12, "bold"), width=100, height=35, command=self.save_customer).grid(row=0, column=4, padx=20)

        tree_frame = tk.Frame(self.content, bg="white")
        tree_frame.pack(pady=20, padx=30, fill="both", expand=True)

        self.cust_tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "Phone"), show='headings')
        for col in ("ID", "Name", "Phone"): self.cust_tree.heading(col, text=col)
        self.cust_tree.pack(fill="both", expand=True)
        self.refresh_customers()

    # --- Start-up Overlay ---
    def show_login_overlay(self):
        self.ov = ctk.CTkFrame(self.root, fg_color="#0a3d62")
        self.ov.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Fixed constructor (No padx/pady here)
        card = ctk.CTkFrame(self.ov, fg_color="white", corner_radius=15)
        card.place(relx=0.5, rely=0.5, anchor="center")
        
        # Inner layout using standard packing
        inner_frame = tk.Frame(card, bg="white")
        inner_frame.pack(padx=50, pady=50) # Safe to use padding here
        
        ctk.CTkLabel(inner_frame, text="👤", font=("Segoe UI", 40), text_color="#0a3d62").pack(pady=(0, 10))
        ctk.CTkLabel(inner_frame, text="LOGIN", font=("Segoe UI", 18, "bold"), text_color="#0a3d62").pack(pady=(0, 20))
        
        ctk.CTkLabel(inner_frame, text="Customer Name:", text_color="#7f8c8d").pack(anchor="w")
        self.oname = ctk.CTkEntry(inner_frame, placeholder_text="Customer Name", width=250, height=40)
        self.oname.pack(pady=(5, 15))
        
        ctk.CTkLabel(inner_frame, text="Phone (for registry):", text_color="#7f8c8d").pack(anchor="w")
        self.onum = ctk.CTkEntry(inner_frame, placeholder_text="Phone Number", width=250, height=40)
        self.onum.pack(pady=(5, 25))
        
        ctk.CTkButton(inner_frame, text="ACCESS SYSTEM", font=("Segoe UI", 14, "bold"), height=45, fg_color="#0a3d62", command=self.submit_login).pack()

    # --- DB Methods ---
    def save_to_inventory(self):
        v = [i.get() for i in self.inv_entries]
        if all(v):
            self.cur.execute("INSERT OR REPLACE INTO inventory (name, p_rate, s_rate, stock) VALUES (?,?,?,?)", (v[0].lower(), v[1], v[2], v[3]))
            self.conn.commit(); self.refresh_inventory()
            for i in self.inv_entries: i.delete(0, 'end')

    def save_customer(self):
        n, p = self.reg_name.get(), self.reg_phone.get()
        if n and p:
            try:
                self.cur.execute("INSERT INTO customers (name, phone) VALUES (?,?)", (n, p))
                self.conn.commit(); self.refresh_customers()
                self.reg_name.delete(0, 'end'); self.reg_phone.delete(0, 'end')
            except: messagebox.showerror("Duplicate", "Customer phone already exists.")

    def refresh_inventory(self):
        for i in self.inv_tree.get_children(): self.inv_tree.delete(i)
        self.cur.execute("SELECT * FROM inventory"); [self.inv_tree.insert("", "end", values=r) for r in self.cur.fetchall()]

    def refresh_customers(self):
        for i in self.cust_tree.get_children(): self.cust_tree.delete(i)
        self.cur.execute("SELECT * FROM customers"); [self.cust_tree.insert("", "end", values=r) for r in self.cur.fetchall()]

    def submit_login(self):
        n = self.oname.get().strip()
        if n:
            self.session_customer = {"name": n, "phone": self.onum.get().strip() or "N/A"}
            self.ov.destroy(); self.ui_billing()
            
    def speak(self, txt):
        try: self.engine.say(txt); self.engine.runAndWait()
        except: pass 

if __name__ == "__main__":
    root = ctk.CTk()
    app = NexusPro(root)
    root.mainloop()