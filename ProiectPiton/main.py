import tkinter as tk
from tkinter import ttk, messagebox
from database import *

# =========================
# INIT DB
# =========================
create_foods_table()
populate_default_foods()
create_eaten_table()

# =========================
# COLORS
# =========================
RED = "#E30613"
RED_DARK = "#B8000C"
WHITE = "#FFFFFF"
BG = "#F6F7F9"
TEXT = "#1A1A1A"
GRAY = "#E9EDF2"

# =========================
# WINDOW
# =========================
root = tk.Tk()
root.title("Calorie Tracker")
root.geometry("930x560")
root.minsize(930, 560)
root.resizable(True, True)   # <-- maximize ON
root.configure(bg=BG)

style = ttk.Style()
style.theme_use("clam")

# General
style.configure("TLabel", font=("Segoe UI", 11), background=BG, foreground=TEXT)
style.configure("Header.TLabel", font=("Segoe UI", 20, "bold"), background=BG, foreground=TEXT)
style.configure("Card.TFrame", background=WHITE)
style.configure("TEntry", padding=6)

# Buttons
style.configure("Primary.TButton",
                font=("Segoe UI", 11, "bold"),
                padding=10,
                background=RED,
                foreground=WHITE)
style.map("Primary.TButton",
          background=[("active", RED_DARK)],
          foreground=[("active", WHITE)])

style.configure("Danger.TButton",
                font=("Segoe UI", 11, "bold"),
                padding=10,
                background=RED_DARK,
                foreground=WHITE)
style.map("Danger.TButton",
          background=[("active", RED)],
          foreground=[("active", WHITE)])

# Combobox
style.configure("TCombobox", padding=6)

# Treeview
style.configure("Treeview",
                font=("Segoe UI", 11),
                rowheight=30,
                background=WHITE,
                fieldbackground=WHITE,
                foreground=TEXT,
                bordercolor=GRAY,
                borderwidth=1)
style.configure("Treeview.Heading",
                font=("Segoe UI", 11, "bold"),
                background=GRAY,
                foreground=TEXT)
style.map("Treeview",
          background=[("selected", "#DDE8FF")],
          foreground=[("selected", TEXT)])

# =========================
# FUNCTIONS
# =========================
def refresh_foods():
    foods = [f[0] for f in get_all_foods()]
    food_combo["values"] = foods
    if foods and not food_var.get():
        food_var.set(foods[0])

def refresh_eaten():
    for row in tree.get_children():
        tree.delete(row)

    for row in get_all_eaten():
        tree.insert("", "end", values=row)

    total_lbl.config(text=f"{total_calories():.0f} kcal")

def add_food_ui():
    food = food_var.get().strip()
    grams_txt = grams_entry.get().strip()

    if not food or not grams_txt:
        messagebox.showerror("Eroare", "Completează alimentul și gramajul.")
        return

    try:
        grams = float(grams_txt)
        if grams <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Eroare", "Gramaj invalid. Exemplu: 150")
        return

    cal_100 = get_calories_per_100g(food)
    if cal_100 is None:
        messagebox.showerror("Eroare", "Aliment inexistent în baza de date.")
        return

    calories = (cal_100 * grams) / 100
    add_eaten(food, grams, calories)

    grams_entry.delete(0, tk.END)
    refresh_eaten()

def delete_selected():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Atenție", "Selectează un rând din listă.")
        return

    eaten_id = tree.item(selected[0])["values"][0]
    ok = delete_eaten_by_id_safe(eaten_id)
    if not ok:
        messagebox.showerror("Eroare", f"Nu am găsit ID-ul {eaten_id} în baza de date.")
    refresh_eaten()

def delete_by_id_ui():
    txt = id_entry.get().strip()
    if not txt:
        messagebox.showwarning("Atenție", "Scrie un ID.")
        return

    try:
        eid = int(txt)
        if eid <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Eroare", "ID invalid. Exemplu: 3")
        return

    ok = delete_eaten_by_id_safe(eid)
    if not ok:
        messagebox.showerror("Eroare", f"Nu există ID-ul {eid} în baza de date.")
        return

    id_entry.delete(0, tk.END)
    refresh_eaten()

def on_enter_add(event):
    add_food_ui()

# =========================
# HEADER BAR
# =========================
header_wrap = ttk.Frame(root, style="Card.TFrame", padding=14)
header_wrap.pack(fill="x", padx=18, pady=(18, 10))

accent = tk.Frame(header_wrap, bg=RED, width=8, height=1)
accent.pack(side="left", fill="y")

header_txt = ttk.Label(header_wrap, text="Calorie Tracker", style="Header.TLabel", background=WHITE)
header_txt.pack(side="left", padx=(12, 0))

# (am scos subtitlul "PENNY vibe ...")

# =========================
# TOP CARD (ADD)
# =========================
top_card = ttk.Frame(root, style="Card.TFrame", padding=16)
top_card.pack(fill="x", padx=18, pady=10)

ttk.Label(top_card, text="Aliment", background=WHITE).grid(row=0, column=0, sticky="w", padx=6, pady=(0, 6))
ttk.Label(top_card, text="Gramaj (g)", background=WHITE).grid(row=0, column=1, sticky="w", padx=6, pady=(0, 6))

food_var = tk.StringVar()
food_combo = ttk.Combobox(top_card, textvariable=food_var, state="readonly", width=35)
food_combo.grid(row=1, column=0, padx=6, pady=4, sticky="we")

grams_entry = ttk.Entry(top_card, width=14)
grams_entry.grid(row=1, column=1, padx=6, pady=4, sticky="w")
grams_entry.bind("<Return>", on_enter_add)

add_btn = ttk.Button(top_card, text="Adaugă", style="Primary.TButton", command=add_food_ui)
add_btn.grid(row=1, column=2, padx=(14, 6), pady=4)

top_card.columnconfigure(0, weight=1)

# =========================
# TABLE CARD
# =========================
table_card = ttk.Frame(root, style="Card.TFrame", padding=14)
table_card.pack(fill="both", expand=True, padx=18, pady=10)

columns = ("ID", "Aliment", "Gramaj (g)", "Calorii")
tree = ttk.Treeview(table_card, columns=columns, show="headings")

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center")

tree.column("ID", width=70)
tree.column("Aliment", width=420, anchor="w")
tree.column("Gramaj (g)", width=140)
tree.column("Calorii", width=140)

tree.pack(side="left", fill="both", expand=True)

scroll = ttk.Scrollbar(table_card, orient="vertical", command=tree.yview)
scroll.pack(side="right", fill="y")
tree.configure(yscrollcommand=scroll.set)

# =========================
# FOOTER (DELETE + DELETE ID + TOTAL)
# =========================
footer = ttk.Frame(root, style="Card.TFrame", padding=14)
footer.pack(fill="x", padx=18, pady=(10, 18))

# delete selected
delete_btn = ttk.Button(footer, text="Șterge selectat", style="Danger.TButton", command=delete_selected)
delete_btn.pack(side="left")

# delete by ID (NEW)
delete_id_wrap = tk.Frame(footer, bg=WHITE)
delete_id_wrap.pack(side="left", padx=12)

ttk.Label(delete_id_wrap, text="ID:", background=WHITE).pack(side="left", padx=(0, 6))
id_entry = ttk.Entry(delete_id_wrap, width=8)
id_entry.pack(side="left", padx=(0, 8))

delete_id_btn = ttk.Button(delete_id_wrap, text="Șterge ID", style="Danger.TButton", command=delete_by_id_ui)
delete_id_btn.pack(side="left")

# total (UPDATED)
total_wrap = tk.Frame(footer, bg=WHITE)
total_wrap.pack(side="right")

ttk.Label(total_wrap, text="TOTAL CALORII", background=WHITE, foreground="#666666",
          font=("Segoe UI", 10, "bold")).pack(anchor="e")
total_lbl = ttk.Label(total_wrap, text="0 kcal", background=WHITE, foreground=TEXT,
                      font=("Segoe UI", 18, "bold"))
total_lbl.pack(anchor="e")

# =========================
# START
# =========================
refresh_foods()
refresh_eaten()
root.mainloop()
