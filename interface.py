import socket, threading, re, tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
HEADER_LENGTH = 10
SERVER_IP, SERVER_PORT = "localhost", 8000

class ChatClient:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((SERVER_IP, SERVER_PORT))
        self.window = tk.Tk()
        self.window.title("Support Chat Client")
        self.window.geometry = "800x600"

        self.message_display = scrolledtext.ScrolledText(self.window, state='disabled', width=70, height=25)
        self.message_display.pack()
        self.message_input = tk.Entry(self.window)
        self.message_input.pack()
        self.message_input.bind("<Return>", self.send_message)

        self.get_user_info()
        threading.Thread(target=self.receive_messages, daemon=True).start()
        self.window.mainloop()

    def get_user_info(self):
        name = self.ask_valid_input("Please Enter Your Name:", self.is_valid_name, "Name must be alphabetic characters only.")
        number = self.ask_valid_input("Please Enter Your Registered Mobile Number (10 digits):", self.is_valid_phone_number, "Phone number must be a 10-digit number.")
        issue = self.select_issue()
        self.send_message_to_server(f"Name: {name}\nNumber: {number}\nIssue: {issue}\nstart")

    def ask_valid_input(self, prompt, validation_func, error_msg):
        while True:
            value = simpledialog.askstring("Input", prompt, parent=self.window)
            if value and validation_func(value):
                return value
            messagebox.showerror("Invalid Input", error_msg)

    def select_issue(self):
        issues = ["Wrong Product Received", "Return Product", "Request for Exchange", "Damaged Product", "Order ID/Invoice Identification", "Payment Problem", "Other"]
        choice = simpledialog.askinteger("Select Issue", "\n".join([f"{i+1}. {issue}" for i, issue in enumerate(issues)]), parent=self.window)
        print(choice)
        return issues[choice-1 if not choice > 7 else 6]


    def is_valid_name(self, name): return re.match(r'^[A-Za-z\s]+$', name) is not None
    def is_valid_phone_number(self, number): return re.match(r'^\d{10}$', number) is not None
    def send_message(self, event=None): self.send_message_to_server(self.message_input.get()); self.message_input.delete(0, tk.END)
    def send_message_to_server(self, msg): self.client_socket.send(f"{len(msg):<{HEADER_LENGTH}}".encode() + msg.encode())
    def receive_messages(self):
        while True:
            try:
                message_header = self.client_socket.recv(HEADER_LENGTH)
                if not message_header: break
                message_length = int(message_header.decode().strip())
                message = self.client_socket.recv(message_length).decode()
                self.display_message(f"\nReceived message: {message}")
            except: break
        self.client_socket.close()

    def display_message(self, message):
        self.message_display.config(state='normal'); self.message_display.insert(tk.END, message + "\n")
        self.message_display.config(state='disabled'); self.message_display.see(tk.END)

if __name__ == "__main__": ChatClient()
