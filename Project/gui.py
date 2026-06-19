import tkinter as tk
from tkinter import ttk, messagebox
import database as db

class CollectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Collection Manager")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        self.selected_id = None
        db.create_tables()
        self.build_ui()
        self.load_items()

    def build_ui(self):
        toolbar = tk.Frame(self.root, pady=6, padx=10)
        toolbar.pack(fill="x")

        tk.Label(toolbar, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self.search())
        tk.Entry(toolbar, textvariable=self.search_var, width=25).pack(side="left", padx=5)
        tk.Button(toolbar, text="Clear", command=self.clear_search).pack(side="left")
        tk.Button(toolbar, text="Refresh", command=self.load_items).pack(side="left", padx=5)
        tk.Button(toolbar, text="Reports", bg="#9C27B0", fg="white", command=self.open_reports).pack(side="left", padx=5)
        tk.Button(toolbar, text="Import CSV", bg="#FF9800", fg="white", command=self.import_csv).pack(side="left", padx=5)

        main = tk.Frame(self.root)
        main.pack(fill="both", expand=True, padx=10, pady=5)

        table_frame = tk.Frame(main)
        table_frame.pack(side="left", fill="both", expand=True)

        columns = ("ID", "Title", "Genre", "Year", "Rating", "Date Added")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.column("ID",         width=40,  anchor="center")
        self.tree.column("Title",      width=180)
        self.tree.column("Genre",      width=100)
        self.tree.column("Year",       width=60,  anchor="center")
        self.tree.column("Rating",     width=60,  anchor="center")
        self.tree.column("Date Added", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        form = tk.LabelFrame(main, text="Item Details", padx=10, pady=10, width=250)
        form.pack(side="right", fill="y", padx=(10, 0))
        form.pack_propagate(False)

        fields = ["Title", "Genre", "Year", "Rating", "Notes"]
        self.entries = {}
        for field in fields:
            tk.Label(form, text=field + ":").pack(anchor="w")
            if field == "Notes":
                widget = tk.Text(form, height=4, width=28)
                widget.pack(fill="x", pady=(0, 8))
            else:
                widget = tk.Entry(form, width=28)
                widget.pack(fill="x", pady=(0, 8))
            self.entries[field] = widget

        btn_frame = tk.Frame(form)
        btn_frame.pack(fill="x", pady=(10, 0))
        tk.Button(btn_frame, text="Add",    bg="#4CAF50", fg="white", width=8, command=self.add_item).pack(side="left", padx=2)
        tk.Button(btn_frame, text="Update", bg="#2196F3", fg="white", width=8, command=self.update_item).pack(side="left", padx=2)
        tk.Button(btn_frame, text="Delete", bg="#f44336", fg="white", width=8, command=self.delete_item).pack(side="left", padx=2)
        tk.Button(form, text="Clear Form", width=26, command=self.clear_form).pack(pady=(8, 0))

        self.status = tk.StringVar(value="Ready")
        tk.Label(self.root, textvariable=self.status, anchor="w",
                 relief="sunken", pady=3, padx=5).pack(fill="x", side="bottom")

    def get_form_values(self):
        title  = self.entries["Title"].get().strip()
        genre  = self.entries["Genre"].get().strip()
        year   = self.entries["Year"].get().strip()
        rating = self.entries["Rating"].get().strip()
        notes  = self.entries["Notes"].get("1.0", "end").strip()
        return title, genre, year, rating, notes

    def validate(self, title, year, rating):
        if not title:
            messagebox.showerror("Error", "Title is required.")
            return False
        if year and not year.isdigit():
            messagebox.showerror("Error", "Year must be a number.")
            return False
        if rating:
            try:
                r = float(rating)
                if not (0 <= r <= 10):
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Rating must be a number between 0 and 10.")
                return False
        return True

    def load_items(self):
        self.tree.delete(*self.tree.get_children())
        for row in db.get_all_items():
            self.tree.insert("", "end", iid=row["id"], values=(
                row["id"], row["title"], row["genre"] or "",
                row["year"] or "", row["rating"] or "", row["date_added"] or ""
            ))
        self.status.set(f"{len(self.tree.get_children())} items loaded")

    def on_select(self, event):
        selected = self.tree.focus()
        if not selected:
            return
        self.selected_id = int(selected)
        vals = self.tree.item(selected, "values")
        self.clear_form()
        self.entries["Title"].insert(0, vals[1])
        self.entries["Genre"].insert(0, vals[2])
        self.entries["Year"].insert(0, vals[3])
        self.entries["Rating"].insert(0, vals[4])
        self.status.set(f"Selected: {vals[1]}")

    def add_item(self):
        title, genre, year, rating, notes = self.get_form_values()
        if not self.validate(title, year, rating):
            return
        db.add_item(title, genre, int(year) if year else None,
                    float(rating) if rating else None, notes)
        self.load_items()
        self.clear_form()
        self.status.set(f"Added: {title}")

    def update_item(self):
        if not self.selected_id:
            selected = self.tree.focus()
            if selected:
                self.selected_id = int(selected)
            else:
                messagebox.showwarning("Warning", "Please select an item to update.")
                return
        title, genre, year, rating, notes = self.get_form_values()
        if not self.validate(title, year, rating):
            return
        db.update_item(self.selected_id, title, genre,
                       int(year) if year else None,
                       float(rating) if rating else None, notes)
        self.load_items()
        self.clear_form()
        self.status.set(f"Updated: {title}")

    def delete_item(self):
        if not self.selected_id:
            selected = self.tree.focus()
            if selected:
                self.selected_id = int(selected)
            else:
                messagebox.showwarning("Warning", "Please select an item to delete.")
                return
        if messagebox.askyesno("Confirm", "Delete this item?"):
            db.delete_item(self.selected_id)
            self.load_items()
            self.clear_form()
            self.status.set("Item deleted")

    def search(self):
        keyword = self.search_var.get().strip()
        if not keyword:
            self.load_items()
            return
        self.tree.delete(*self.tree.get_children())
        for row in db.search_items(keyword):
            self.tree.insert("", "end", iid=row["id"], values=(
                row["id"], row["title"], row["genre"] or "",
                row["year"] or "", row["rating"] or "", row["date_added"] or ""
            ))
        self.status.set(f"{len(self.tree.get_children())} results found")

    def clear_search(self):
        self.search_var.set("")
        self.load_items()

    def clear_form(self):
        self.selected_id = None
        for field, widget in self.entries.items():
            if isinstance(widget, tk.Text):
                widget.delete("1.0", "end")
            else:
                widget.delete(0, "end")

    def open_reports(self):
        from reports import ReportsWindow
        ReportsWindow(self.root)

    def import_csv(self):
        from etl import import_from_csv
        import_from_csv(self.load_items)