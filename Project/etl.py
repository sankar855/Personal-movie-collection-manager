import pandas as pd
import database as db
from tkinter import filedialog, messagebox

def import_from_csv(refresh_callback):
    path = filedialog.askopenfilename(
        title="Select CSV file",
        filetypes=[("CSV files", "*.csv")]
    )
    if not path:
        return

    try:
        df = pd.read_csv(path)
        required = {"title"}
        if not required.issubset(set(df.columns.str.lower())):
            messagebox.showerror("Error", "CSV must have at least a 'title' column.")
            return

        df.columns = df.columns.str.lower()
        count = 0
        for _, row in df.iterrows():
            title  = str(row.get("title",  "")).strip()
            genre  = str(row.get("genre",  "")).strip()
            year   = row.get("year",   None)
            rating = row.get("rating", None)
            notes  = str(row.get("notes",  "")).strip()

            if not title or title.lower() == "nan":
                continue
            try:
                year   = int(year)   if year   and str(year)   != "nan" else None
                rating = float(rating) if rating and str(rating) != "nan" else None
            except (ValueError, TypeError):
                year, rating = None, None

            db.add_item(title, genre or None, year, rating, notes or None)
            count += 1

        messagebox.showinfo("Import Complete", f"Successfully imported {count} items!")
        refresh_callback()

    except Exception as e:
        messagebox.showerror("Import Error", f"Something went wrong:\n{e}")