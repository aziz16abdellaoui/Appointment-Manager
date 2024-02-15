import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime
import random

class AppointmentManager:
    def __init__(self, root, user_type):
        self.root = root
        self.user_type = user_type
        if user_type == "Doctor":
            self.root.title("Doctor Appointment Manager")
            title_text = "Hi Doctor, Welcome to Appointment Manager"
        elif user_type == "Patient":
            self.root.title("Patient Appointment Manager")
            title_text = "Hi Patient, Welcome to Appointment Manager"
        else:
            messagebox.showerror("Error", "Invalid user type.")
            self.root.destroy()
            return
        self.root.geometry("800x500")
        self.root.config(bg="#F0F0F0")

        self.name_var = tk.StringVar()
        self.contact_var = tk.StringVar()
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))  # Default value is current date
        self.time_var = tk.StringVar(value=datetime.now().strftime("%H:%M"))  # Default value is current time

        # Database
        self.conn = sqlite3.connect("appointments.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS appointments (id INTEGER PRIMARY KEY, name TEXT, contact TEXT, date TEXT, time TEXT, user_type TEXT)")
        self.conn.commit()

        # Ensure all required columns are added to the appointments table
        self.cursor.execute("PRAGMA table_info(appointments)")
        columns = self.cursor.fetchall()
        column_names = [column[1] for column in columns]
        if "name" not in column_names:
            self.cursor.execute("ALTER TABLE appointments ADD COLUMN name TEXT")
        if "contact" not in column_names:
            self.cursor.execute("ALTER TABLE appointments ADD COLUMN contact TEXT")
        if "date" not in column_names:
            self.cursor.execute("ALTER TABLE appointments ADD COLUMN date TEXT")
        if "time" not in column_names:
            self.cursor.execute("ALTER TABLE appointments ADD COLUMN time TEXT")
        if "user_type" not in column_names:
            self.cursor.execute("ALTER TABLE appointments ADD COLUMN user_type TEXT")
        self.conn.commit()

        # Title
        title_label = tk.Label(root, text=title_text, font=("Helvetica", 24), bg="#333", fg="#FFF", padx=10, pady=5)
        title_label.pack(fill="x")

        if user_type == "Patient":
            # Add appointment frame
            add_frame = ttk.Frame(root, padding=20)
            add_frame.pack(pady=20)

            # Labels and Entries for adding appointments
            ttk.Label(add_frame, text="Name:", font=("Helvetica", 12)).grid(row=0, column=0, sticky="w", pady=5)
            ttk.Entry(add_frame, textvariable=self.name_var, font=("Helvetica", 12)).grid(row=0, column=1, padx=10)
            ttk.Label(add_frame, text="Contact:", font=("Helvetica", 12)).grid(row=1, column=0, sticky="w", pady=5)
            ttk.Entry(add_frame, textvariable=self.contact_var, font=("Helvetica", 12)).grid(row=1, column=1, padx=10)
            ttk.Label(add_frame, text="Date:", font=("Helvetica", 12)).grid(row=2, column=0, sticky="w", pady=5)
            ttk.Entry(add_frame, textvariable=self.date_var, font=("Helvetica", 12)).grid(row=2, column=1, padx=10)
            ttk.Label(add_frame, text="Time:", font=("Helvetica", 12)).grid(row=3, column=0, sticky="w", pady=5)
            ttk.Entry(add_frame, textvariable=self.time_var, font=("Helvetica", 12)).grid(row=3, column=1, padx=10)

            ttk.Button(add_frame, text="Make Appointment", command=self.make_appointment).grid(row=4, column=0, columnspan=2, pady=10)

            # Add cancel appointment button
            ttk.Button(root, text="Cancel Appointment", command=self.cancel_appointment).pack()

        # Buttons for exit
        action_buttons = ttk.Frame(root)
        action_buttons.pack()
        if user_type == "Doctor":
            ttk.Button(action_buttons, text="Delete Appointment", command=self.delete_appointment).pack(side="left", padx=10)
        ttk.Button(action_buttons, text="Exit", command=self.exit_program).pack(side="right", padx=10)

        # Appointments treeview
        self.appointments_tree = ttk.Treeview(root, columns=("Index", "Name", "Contact", "Date", "Time"), show="headings", height=15)
        self.appointments_tree.pack(pady=20)
        self.appointments_tree.heading("Index", text="Index")
        self.appointments_tree.heading("Name", text="Name")
        self.appointments_tree.heading("Contact", text="Contact")
        self.appointments_tree.heading("Date", text="Date")
        self.appointments_tree.heading("Time", text="Time")
        self.appointments_tree.column("#0", width=0, stretch=tk.NO)  # Hide index column

        # Supportive quote from doctor
        supportive_quote_label = ttk.Label(root, text=self.get_supportive_quote(), font=("Helvetica", 12), wraplength=600)
        supportive_quote_label.pack(pady=10)

        # Load existing appointments
        self.load_appointments()

    def make_appointment(self):
        name = self.name_var.get()
        contact = self.contact_var.get()
        date = self.date_var.get()
        time = self.time_var.get()

        if name and contact and date and time:
            self.cursor.execute("INSERT INTO appointments (name, contact, date, time, user_type) VALUES (?, ?, ?, ?, ?)", (name, contact, date, time, self.user_type))
            self.conn.commit()
            self.load_appointments()  # Reload appointments after adding a new one
            self.clear_entries()
        else:
            messagebox.showerror("Error", "Please fill all fields.")

    def exit_program(self):
        self.root.destroy()

    def load_appointments(self):
        self.appointments_tree.delete(*self.appointments_tree.get_children())
        if self.user_type == "Doctor":
            self.cursor.execute("SELECT rowid, name, contact, date, time FROM appointments WHERE user_type='Patient'")
        elif self.user_type == "Patient":
            self.cursor.execute("SELECT rowid, name, contact, date, time FROM appointments WHERE name=?", (self.name_var.get(),))
        appointments = self.cursor.fetchall()
        for appointment in appointments:
            self.appointments_tree.insert("", "end", values=(appointment[0], appointment[1], appointment[2], appointment[3], appointment[4]))

    def clear_entries(self):
        self.name_var.set("")
        self.contact_var.set("")
        self.date_var.set(datetime.now().strftime("%Y-%m-%d"))  # Reset date entry field to current date
        self.time_var.set(datetime.now().strftime("%H:%M"))  # Reset time entry field to current time

    def cancel_appointment(self):
        selected_item = self.appointments_tree.selection()
        if selected_item:
            appointment_details = self.appointments_tree.item(selected_item)['values']
            if appointment_details:
                confirmation = messagebox.askyesno("Confirm Cancellation", "Are you sure you want to cancel this appointment?")
                if confirmation:
                    name, contact, date, time = appointment_details
                    self.cursor.execute("DELETE FROM appointments WHERE name=? AND contact=? AND date=? AND time=?", (name, contact, date, time))
                    self.conn.commit()
                    self.load_appointments()
        else:
            messagebox.showwarning("No Selection", "Please select an appointment to cancel.")

    def delete_appointment(self):
        selected_item = self.appointments_tree.selection()
        if selected_item:
            appointment_details = self.appointments_tree.item(selected_item)['values']
            if appointment_details:
                confirmation = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this appointment?")
                if confirmation:
                    name, contact, date, time = appointment_details
                    self.cursor.execute("DELETE FROM appointments WHERE name=? AND contact=? AND date=? AND time=?", (name, contact, date, time))
                    self.conn.commit()
                    self.load_appointments()
        else:
            messagebox.showwarning("No Selection", "Please select an appointment to delete.")

    def get_supportive_quote(self):
       
        quotes = [
            "Remember, your health is your wealth!",
            "Stay positive and keep pushing forward. You're stronger than you think!",
            "Every journey starts with a single step. Keep moving forward!",
            "Don't forget to take care of yourself. You deserve it!"
        ]
        return random.choice(quotes)

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("400x250")

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.user_type_var = tk.StringVar(value="Patient")  # Default user type is Patient

        login_frame = ttk.Frame(root, padding=20)
        login_frame.pack()

        ttk.Label(login_frame, text="Username:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(login_frame, textvariable=self.username_var).grid(row=0, column=1, padx=10)

        ttk.Label(login_frame, text="Password:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(login_frame, textvariable=self.password_var, show="*").grid(row=1, column=1, padx=10)

        ttk.Label(login_frame, text="User Type:").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Radiobutton(login_frame, text="Doctor", variable=self.user_type_var, value="Doctor").grid(row=2, column=1, padx=10)
        ttk.Radiobutton(login_frame, text="Patient", variable=self.user_type_var, value="Patient").grid(row=2, column=2, padx=10)

        ttk.Button(login_frame, text="Login", command=self.login).grid(row=3, column=0, pady=10)
        ttk.Button(login_frame, text="Sign Up", command=self.signup).grid(row=3, column=1, pady=10)

        self.conn = sqlite3.connect("users.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, user_type TEXT)")
        self.conn.commit()

    def login(self):
        username = self.username_var.get()
        password = self.password_var.get()
        user_type = self.user_type_var.get()

        if username and password and user_type:
            self.cursor.execute("SELECT * FROM users WHERE username=? AND user_type=?", (username, user_type))
            user = self.cursor.fetchone()
            if user:
                if user[1] == password:
                    self.root.destroy()
                    root = tk.Tk()
                    app = AppointmentManager(root, user_type)
                    root.mainloop()
                else:
                    messagebox.showerror("Error", "Incorrect password.")
            else:
                messagebox.showerror("Error", "Username not found. Please create an account.")
        else:
            messagebox.showerror("Error", "Please enter both username and password.")

    def signup(self):
        self.root.destroy()  # Close login window before opening signup window
        signup_window = tk.Tk()
        signup_app = SignupWindow(signup_window)
        signup_window.mainloop()

class SignupWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Sign Up")
        self.root.geometry("400x250")

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.user_type_var = tk.StringVar(value="Patient") 

        signup_frame = ttk.Frame(root, padding=20)
        signup_frame.pack()

        ttk.Label(signup_frame, text="Username:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(signup_frame, textvariable=self.username_var).grid(row=0, column=1, padx=10)

        ttk.Label(signup_frame, text="Password:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(signup_frame, textvariable=self.password_var, show="*").grid(row=1, column=1, padx=10)

        ttk.Label(signup_frame, text="User Type:").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Radiobutton(signup_frame, text="Doctor", variable=self.user_type_var, value="Doctor").grid(row=2, column=1, padx=10)
        ttk.Radiobutton(signup_frame, text="Patient", variable=self.user_type_var, value="Patient").grid(row=2, column=2, padx=10)

        ttk.Button(signup_frame, text="Sign Up", command=self.signup).grid(row=3, column=0, pady=10)

        self.conn = sqlite3.connect("users.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, user_type TEXT)")
        self.conn.commit()

    def signup(self):
        username = self.username_var.get()
        password = self.password_var.get()
        user_type = self.user_type_var.get()

        if username and password and user_type:
            self.cursor.execute("SELECT * FROM users WHERE username=?", (username,))
            user = self.cursor.fetchone()
            if user:
                messagebox.showerror("Error", "Username already exists.")
            else:
                self.cursor.execute("INSERT INTO users (username, password, user_type) VALUES (?, ?, ?)", (username, password, user_type))
                self.conn.commit()
                messagebox.showinfo("Success", "Account created successfully!")
                self.root.destroy() 
                login_window = tk.Tk()
                login_app = LoginWindow(login_window)
                login_window.mainloop()
        else:
            messagebox.showerror("Error", "Please fill all fields.")

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()
