import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import database as db
import pandas as pd

class ReportsWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Reports & Export")
        self.window.geometry("800x550")
        self.build_ui()
        self.load_report()

    def build_ui(self):
        # ── Filter bar ──
        filter_frame = tk.LabelFrame(self.window, text="Filters", padx=8, pady=6)
        filter_frame.pack(fill="x", padx=10, pady=8)

        tk.Label(filter_frame, text="Genre:").grid(row=0, column=0, padx=4)
        self.genre_var = tk.StringVar(value="All")
        self.genre_cb = ttk.Combobox(filter_frame, textvariable=self.genre_var, width=14, state="readonly")
        self.genre_cb.grid(row=0, column=1, padx=4)

        tk.Label(filter_frame, text="Min Rating:").grid(row=0, column=2, padx=4)
        self.min_rating = tk.StringVar(value="0")
        tk.Entry(filter_frame, textvariable=self.min_rating, width=6).grid(row=0, column=3, padx=4)

        tk.Label(filter_frame, text="Sort by:").grid(row=0, column=4, padx=4)
        self.sort_var = tk.StringVar(value="date_added")
        sort_cb = ttk.Combobox(filter_frame, textvariable=self.sort_var, width=12, state="readonly",
                               values=["title", "genre", "year", "rating", "date_added"])
        sort_cb.grid(row=0, column=5, padx=4)

        tk.Button(filter_frame, text="Apply", command=self.load_report).grid(row=0, column=6, padx=8)
        tk.Button(filter_frame, text="Reset",  command=self.reset_filters).grid(row=0, column=7, padx=4)

        # ── Summary stats ──
        self.stats_frame = tk.Frame(self.window)
        self.stats_frame.pack(fill="x", padx=10, pady=4)
        self.stat_vars = {}
        for label in ["Total Items", "Avg Rating", "Genres", "Newest Year"]:
            card = tk.Frame(self.stats_frame, relief="groove", bd=1, padx=12, pady=6)
            card.pack(side="left", padx=6)
            tk.Label(card, text=label, font=("Arial", 8), fg="gray").pack()
            var = tk.StringVar(value="-")
            tk.Label(card, textvariable=var, font=("Arial", 14, "bold")).pack()
            self.stat_vars[label] = var

        # ── Results table ──
        table_frame = tk.Frame(self.window)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        cols = ("ID", "Title", "Genre", "Year", "Rating", "Date Added")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=14)
        for col in cols:
            self.tree.heading(col, text=col)
        self.tree.column("ID",         width=40,  anchor="center")
        self.tree.column("Title",      width=200)
        self.tree.column("Genre",      width=100)
        self.tree.column("Year",       width=60,  anchor="center")
        self.tree.column("Rating",     width=60,  anchor="center")
        self.tree.column("Date Added", width=100, anchor="center")

        sb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # ── Export button ──
        tk.Button(self.window, text="Export to CSV", bg="#4CAF50", fg="white",
                  font=("Arial", 10), pady=4, command=self.export_csv).pack(pady=8)

    def load_report(self):
        rows = db.get_all_items()

        # Populate genre dropdown
        genres = sorted(set(r["genre"] for r in rows if r["genre"]))
        self.genre_cb["values"] = ["All"] + genres

        # Apply filters
        genre = self.genre_var.get()
        try:
            min_r = float(self.min_rating.get())
        except ValueError:
            min_r = 0

        filtered = []
        for r in rows:
            if genre != "All" and r["genre"] != genre:
                continue
            if r["rating"] and float(r["rating"]) < min_r:
                continue
            filtered.append(r)

        # Sort
        sort_key = self.sort_var.get()
        filtered.sort(key=lambda r: (r[sort_key] or ""), reverse=(sort_key == "rating"))

        # Update table
        self.tree.delete(*self.tree.get_children())
        for r in filtered:
            self.tree.insert("", "end", values=(
                r["id"], r["title"], r["genre"] or "",
                r["year"] or "", r["rating"] or "", r["date_added"] or ""
            ))

        # Update stat cards
        total = len(filtered)
        ratings = [float(r["rating"]) for r in filtered if r["rating"]]
        avg = round(sum(ratings) / len(ratings), 1) if ratings else "-"
        unique_genres = len(set(r["genre"] for r in filtered if r["genre"]))
        years = [r["year"] for r in filtered if r["year"]]
        newest = max(years) if years else "-"

        self.stat_vars["Total Items"].set(total)
        self.stat_vars["Avg Rating"].set(avg)
        self.stat_vars["Genres"].set(unique_genres)
        self.stat_vars["Newest Year"].set(newest)

    def reset_filters(self):
        self.genre_var.set("All")
        self.min_rating.set("0")
        self.sort_var.set("date_added")
        self.load_report()

    def export_csv(self):
        rows = db.get_all_items()
        if not rows:
            messagebox.showinfo("Info", "No items to export.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="my_collection.csv"
        )
        if not path:
            return
        df = pd.DataFrame([dict(r) for r in rows])
        df.to_csv(path, index=False)
        messagebox.showinfo("Exported", f"Saved to:\n{path}")
