import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from tkcalendar import DateEntry
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

CSV_FILE = "expenses.csv"


if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=["Date", "Category", "Description", "Amount"]).to_csv(CSV_FILE, index=False)


def save_expense():
    date = date_entry.get()
    category = category_entry.get()
    description = description_entry.get()
    try:
        amount = float(amount_entry.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid amount.")
        return

    if not category:
        messagebox.showerror("Missing Data", "Please enter a category.")
        return

    new_entry = pd.DataFrame([[date, category, description, amount]],
                             columns=["Date", "Category", "Description", "Amount"])
    df = pd.read_csv(CSV_FILE)
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

    messagebox.showinfo("Success", "Expense added successfully.")
    reset_fields()
    update_total()
    update_expense_list()

def update_total():
    df = pd.read_csv(CSV_FILE)
    total = df["Amount"].sum()
    total_label.config(text=f"Total Spend: ₹{total:.2f}")


def show_summary():
    df = pd.read_csv(CSV_FILE)
    if df.empty:
        messagebox.showinfo("No Data", "No expenses to display.")
        return

    plt.figure(figsize=(10, 4))

    plt.subplot(1, 2, 1)
    category_sum = df.groupby("Category")["Amount"].sum()
    category_sum.plot.pie(autopct="%1.1f%%", startangle=140)
    plt.title("Spending by Category")
    plt.ylabel("")

    
    plt.subplot(1, 2, 2)
    df["Date"] = pd.to_datetime(df["Date"])
    daily_sum = df.groupby(df["Date"].dt.date)["Amount"].sum()
    daily_sum.plot.bar()
    plt.title("Daily Spending")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def reset_fields():
    date_entry.set_date(datetime.now())
    category_entry.delete(0, tk.END)
    description_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    expense_tree.selection_remove(expense_tree.selection())


def update_expense_list():
    for row in expense_tree.get_children():
        expense_tree.delete(row)
    df = pd.read_csv(CSV_FILE)
    for _, row in df.iterrows():
        expense_tree.insert("", tk.END, values=(row["Date"], row["Category"], row["Description"], f"₹{row['Amount']:.2f}"))


def clear_all_data():
    confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete all expenses?")
    if confirm:
        pd.DataFrame(columns=["Date", "Category", "Description", "Amount"]).to_csv(CSV_FILE, index=False)
        update_expense_list()
        update_total()
        messagebox.showinfo("Success", "All expenses have been cleared.")


def export_data():
    df = pd.read_csv(CSV_FILE)
    if df.empty:
        messagebox.showinfo("No Data", "No data available to export.")
        return

    option = simpledialog.askstring("Export Format", "Enter format to export (csv/excel):")
    if not option:
        return

    option = option.lower().strip()
    if option not in ["csv", "excel"]:
        messagebox.showerror("Invalid Option", "Please enter 'csv' or 'excel'.")
        return

    filetypes = [("CSV files", "*.csv")] if option == "csv" else [("Excel files", "*.xlsx")]
    ext = ".csv" if option == "csv" else ".xlsx"

    file_path = filedialog.asksaveasfilename(defaultextension=ext, filetypes=filetypes)

    if not file_path:
        return

    try:
        if option == "csv":
            df.to_csv(file_path, index=False)
        else:
            df.to_excel(file_path, index=False)
        messagebox.showinfo("Exported", f"Expenses exported successfully to {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export: {e}")

root = tk.Tk()
root.title("Budget Tracker & Visualizer")
root.geometry("750x700")
root.resizable(True, True)

tk.Label(root, text="Enter Expense Details", font=("Helvetica", 14, "bold"), bg="lightblue").pack(fill=tk.X, pady=10)

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Date:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
date_entry = DateEntry(frame, width=15, background="lightblue", foreground="black", date_pattern="yyyy-mm-dd")
date_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame, text="Category:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
category_entry = ttk.Entry(frame, width=25)
category_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame, text="Description:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
description_entry = ttk.Entry(frame, width=25)
description_entry.grid(row=2, column=1, padx=5, pady=5)

tk.Label(frame, text="Amount (₹):").grid(row=3, column=0, padx=5, pady=5, sticky="e")
amount_entry = ttk.Entry(frame, width=25)
amount_entry.grid(row=3, column=1, padx=5, pady=5)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(button_frame, text="Add Expense", command=save_expense, bg="#4CAF50", fg="black").grid(row=0, column=0, padx=10)
tk.Button(button_frame, text="Reset", command=reset_fields, background="red", fg="black").grid(row=0, column=1, padx=10)
tk.Button(button_frame, text="Show Summary", command=show_summary, bg="orange", fg="black").grid(row=0, column=2, padx=10)
tk.Button(button_frame, text="Clear All Data", command=clear_all_data, bg="lightblue", fg="black").grid(row=0, column=3, padx=10)
tk.Button(button_frame, text="Export Data", command=export_data, bg="gray", fg="black").grid(row=0, column=4, padx=10)

total_label = tk.Label(root, text="Total Spend: ₹0.00", font=("Helvetica", 12))
total_label.pack(pady=10)


tk.Label(root, text="Expense List", font=("Helvetica", 12, "bold")).pack(pady=5)
columns = ("Date", "Category", "Description", "Amount")
expense_tree = ttk.Treeview(root, columns=columns, show="headings", height=12)
for col in columns:
    expense_tree.heading(col, text=col)
    expense_tree.column(col, width=150, anchor="center")
expense_tree.pack(pady=10, fill=tk.BOTH, expand=True)

update_total()
update_expense_list()

root.mainloop()
