import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk  # Added for Treeview
import sqlite3
import os

DB_PATH = "fantasy_cricket.db"

class FantasyCricketGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Fantasy Cricket - Team Selection")
        self.root.geometry("1000x600")

        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

        self.team_name = ""
        self.selected_players = []
        self.points_available = 100
        self.points_used = 0

        self.category_count = {"BAT": 0, "BWL": 0, "AR": 0, "WK": 0}

        self.setup_ui()
        self.insert_default_players()

    def insert_default_players(self):
        default_players = [
            ("Virat Kohli", 250, 12000, 43, 60, 9, "BAT"),
            ("MS Dhoni", 350, 10500, 10, 65, 10, "WK"),
            # ... [Rest of your players here] ...
            ("Rahmanullah Gurbaz", 40, 1200, 2, 6, 8, "WK")
        ]
        for player in default_players:
            self.cursor.execute("INSERT OR IGNORE INTO stats VALUES (?, ?, ?, ?, ?, ?, ?)", player)
        self.conn.commit()

    def setup_ui(self):
        menu = tk.Menu(self.root)
        team_menu = tk.Menu(menu, tearoff=0)
        team_menu.add_command(label="New Team", command=self.new_team)
        team_menu.add_command(label="Save Team", command=self.save_team)
        team_menu.add_command(label="View Saved Teams", command=self.view_saved_teams)
        team_menu.add_command(label="Delete Team", command=self.delete_team)
        team_menu.add_command(label="Modify Team", command=self.modify_team)
        team_menu.add_command(label="Exit", command=self.root.quit)
        menu.add_cascade(label="Team", menu=team_menu)
        self.root.config(menu=menu)

        self.category_var = tk.StringVar()
        category_frame = tk.Frame(self.root)
        category_frame.pack(pady=5)
        for cat in ["BAT", "BWL", "AR", "WK"]:
            tk.Radiobutton(category_frame, text=cat, variable=self.category_var,
                           value=cat, command=self.load_players).pack(side=tk.LEFT)

        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=5)
        tk.Label(search_frame, text="Search Player: ").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT)
        tk.Button(search_frame, text="Go", command=self.load_players).pack(side=tk.LEFT)

        list_frame = tk.Frame(self.root)
        list_frame.pack(pady=10)

        self.available_list = tk.Listbox(list_frame, width=30, height=15)
        self.available_list.grid(row=0, column=0)
        self.available_list.bind("<<ListboxSelect>>", self.show_player_stats)

        button_frame = tk.Frame(list_frame)
        button_frame.grid(row=0, column=1, padx=10)
        tk.Button(button_frame, text=">>>", command=self.add_player).pack(pady=5)
        tk.Button(button_frame, text="<<<", command=self.remove_player).pack(pady=5)

        self.selected_list = tk.Listbox(list_frame, width=30, height=15)
        self.selected_list.grid(row=0, column=2)

        self.stats_text = tk.Text(self.root, width=80, height=5)
        self.stats_text.pack(pady=5)

        self.points_label = tk.Label(self.root, text="Points Available: 100 | Points Used: 0")
        self.points_label.pack(pady=5)

        self.team_label = tk.Label(self.root, text="Team: None", font=("Arial", 12, "bold"))
        self.team_label.pack(pady=5)

    def new_team(self):
        self.team_name = simpledialog.askstring("Team Name", "Enter team name:")
        if self.team_name:
            self.available_list.delete(0, tk.END)
            self.selected_list.delete(0, tk.END)
            self.stats_text.delete("1.0", tk.END)
            self.selected_players.clear()
            self.points_available = 100
            self.points_used = 0
            self.category_count = {"BAT": 0, "BWL": 0, "AR": 0, "WK": 0}
            self.update_points_label()
            self.load_players()
            self.team_label.config(text=f"Team: {self.team_name}")

    def load_players(self):
        cat = self.category_var.get()
        search_term = self.search_var.get().lower()
        self.available_list.delete(0, tk.END)
        if not cat:
            return
        self.cursor.execute("SELECT player FROM stats WHERE ctg=?", (cat,))
        players = self.cursor.fetchall()
        for player in players:
            name = player[0]
            if name not in self.selected_players and search_term in name.lower():
                self.available_list.insert(tk.END, name)

    def show_player_stats(self, event):
        selection = self.available_list.curselection()
        if not selection:
            return
        player = self.available_list.get(selection[0])
        self.cursor.execute("SELECT * FROM stats WHERE player=?", (player,))
        row = self.cursor.fetchone()
        if row:
            text = f"Name: {row[0]}\nMatches: {row[1]}\nRuns: {row[2]}\n100s: {row[3]}\n50s: {row[4]}\nPoints: {row[5]}\nCategory: {row[6]}"
            self.stats_text.delete("1.0", tk.END)
            self.stats_text.insert(tk.END, text)

    def add_player(self):
        selection = self.available_list.curselection()
        if not selection:
            return
        player = self.available_list.get(selection[0])
        self.cursor.execute("SELECT value, ctg FROM stats WHERE player=?", (player,))
        value, cat = self.cursor.fetchone()
        if self.points_used + value > 100:
            messagebox.showwarning("Limit Exceeded", "Not enough points available.")
            return
        if len(self.selected_players) >= 11:
            messagebox.showwarning("Team Full", "You can only select 11 players.")
            return
        self.selected_players.append(player)
        self.selected_list.insert(tk.END, player)
        self.points_used += value
        self.points_available -= value
        self.category_count[cat] += 1
        self.load_players()
        self.update_points_label()

    def remove_player(self):
        selection = self.selected_list.curselection()
        if not selection:
            return
        player = self.selected_list.get(selection[0])
        self.cursor.execute("SELECT value, ctg FROM stats WHERE player=?", (player,))
        value, cat = self.cursor.fetchone()
        self.selected_players.remove(player)
        self.selected_list.delete(selection[0])
        self.points_used -= value
        self.points_available += value
        self.category_count[cat] -= 1
        self.load_players()
        self.update_points_label()

    def update_points_label(self):
        self.points_label.config(text=f"Points Available: {self.points_available} | Points Used: {self.points_used}")

    def save_team(self):
        if not self.team_name:
            messagebox.showerror("No Team", "Please create a new team first.")
            return
        if len(self.selected_players) != 11:
            messagebox.showerror("Invalid Team", "You must select exactly 11 players.")
            return
        if self.category_count['WK'] < 1:
            messagebox.showerror("Missing WK", "You must include at least one Wicket-Keeper.")
            return
        players_str = ','.join(self.selected_players)
        self.cursor.execute("SELECT name FROM teams WHERE name=?", (self.team_name,))
        if self.cursor.fetchone():
            confirm = messagebox.askyesno("Confirm Overwrite", f"Team '{self.team_name}' already exists. Overwrite?")
            if not confirm:
                return
        self.cursor.execute("REPLACE INTO teams (name, players, value) VALUES (?, ?, ?)",
                            (self.team_name, players_str, self.points_used))
        self.conn.commit()
        messagebox.showinfo("Saved", f"Team '{self.team_name}' saved successfully.")

    def delete_team(self):
        team_to_delete = simpledialog.askstring("Delete Team", "Enter the name of the team to delete:")
        if team_to_delete:
            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the team '{team_to_delete}'?")
            if confirm:
                self.cursor.execute("DELETE FROM teams WHERE name=?", (team_to_delete,))
                self.conn.commit()
                messagebox.showinfo("Deleted", f"Team '{team_to_delete}' deleted successfully.")

    def modify_team(self):
        team_to_modify = simpledialog.askstring("Modify Team", "Enter the name of the team to modify:")
        if team_to_modify:
            self.cursor.execute("SELECT players, value FROM teams WHERE name=?", (team_to_modify,))
            row = self.cursor.fetchone()
            if row:
                players, value = row
                self.team_name = team_to_modify
                self.selected_players = players.split(',')
                self.points_used = value
                self.points_available = 100 - value
                self.category_count = {"BAT": 0, "BWL": 0, "AR": 0, "WK": 0}
                self.selected_list.delete(0, tk.END)
                for player in self.selected_players:
                    self.selected_list.insert(tk.END, player)
                    self.cursor.execute("SELECT ctg FROM stats WHERE player=?", (player,))
                    cat_row = self.cursor.fetchone()
                    if cat_row:
                        self.category_count[cat_row[0]] += 1
                self.update_points_label()
                self.load_players()
                self.team_label.config(text=f"Team: {self.team_name}")
            else:
                messagebox.showerror("Error", f"Team '{team_to_modify}' not found.")

    def view_saved_teams(self):
        top = tk.Toplevel(self.root)
        top.title("Saved Teams")
        top.geometry("500x400")

        # Create a Treeview
        tree = ttk.Treeview(top)
        tree.pack(fill=tk.BOTH, expand=True)

        tree["columns"] = ("Details",)
        tree.column("#0", width=200, anchor="w")
        tree.column("Details", width=250, anchor="w")
        tree.heading("#0", text="Team / Player")
        tree.heading("Details", text="Details")

        scrollbar = ttk.Scrollbar(top, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Fetch data and insert
        self.cursor.execute("SELECT name, players FROM teams")
        for row in self.cursor.fetchall():
            team_name = row[0]
            players = [p.strip() for p in row[1].split(",")]

            parent_id = tree.insert("", tk.END, text=team_name)

            for player in players:
                tree.insert(parent_id, tk.END, text=player)

            tree.item(parent_id, open=True)

        # Auto-adjust columns
        tree.update_idletasks()
        for col in ("#0", "Details"):
            tree.column(col, width=tkFont.Font().measure(col))
            max_width = 0
            for item in tree.get_children():
                text = tree.item(item, "text")
                w = tkFont.Font().measure(text)
                if w > max_width:
                    max_width = w
                for child in tree.get_children(item):
                    text = tree.item(child, "text")
                    w = tkFont.Font().measure(text)
                    if w > max_width:
                        max_width = w
            tree.column(col, width=max_width + 20)

import tkinter.font as tkFont

if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        tk.Tk().withdraw()
        messagebox.showerror("Error", "Database not found. Please run setup_database.py first.")
    else:
        root = tk.Tk()
        app = FantasyCricketGUI(root)
        root.mainloop()
