import tkinter as tk
from tkinter import messagebox

# If you have ttkbootstrap installed, uncomment the lines below 
# and replace 'tk' with 'ttk' for a more modern look.
# import ttkbootstrap as ttk

class TipCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("QuickTip Calculator")
        self.root.geometry("350x450")
        
        # --- Variables ---
        # We use Tkinter variables so we can attach "traces" (listeners) to them
        self.bill_amount = tk.StringVar(value="")
        self.tip_percent = tk.DoubleVar(value=15.0)
        self.num_diners = tk.IntVar(value=1)
        
        # --- UI Setup ---
        self.create_widgets()
        
        # --- Event Listeners (Requirement 5) ---
        # These "trace" methods call the calculate function whenever the variable changes
        self.bill_amount.trace_add("write", self.calculate)
        self.tip_percent.trace_add("write", self.calculate)
        self.num_diners.trace_add("write", self.calculate)

    def create_widgets(self):
        """Creates the visual elements of the application."""
        padding = {'padx': 20, 'pady': 10}
        
        # 1. Bill Entry (Requirement 2)
        tk.Label(self.root, text="Total Bill Amount ($):", font=('Arial', 10, 'bold')).pack(**padding)
        self.bill_entry = tk.Entry(self.root, textvariable=self.bill_amount)
        self.bill_entry.pack(pady=5)
        
        # 2. Tip Percentage (Requirement 3 - using a Scale/Slider for better UX)
        tk.Label(self.root, text="Tip Percentage:", font=('Arial', 10, 'bold')).pack(**padding)
        self.tip_slider = tk.Scale(self.root, from_=0, to=50, orient='horizontal', 
                                   variable=self.tip_percent)
        # Set default markers as mentioned in requirements
        self.tip_slider.set(15) 
        self.tip_slider.pack(fill='x', padx=40)
        
        # 3. Number of Diners (Requirement 4 - using a Spinbox)
        tk.Label(self.root, text="Number of Diners:", font=('Arial', 10, 'bold')).pack(**padding)
        self.diner_spin = tk.Spinbox(self.root, from_=1, to=50, textvariable=self.num_diners)
        self.diner_spin.pack(pady=5)

        # --- Display Results ---
        self.result_label = tk.Label(self.root, text="Total per Person: $0.00", 
                                     font=('Arial', 14, 'bold'), fg="green")
        self.result_label.pack(pady=30)
        
        # 4. Quit Button (Requirement 6)
        self.quit_btn = tk.Button(self.root, text="Exit Application", command=self.root.quit, 
                                  bg="#ff6666", fg="white")
        self.quit_btn.pack(side="bottom", pady=20)

    def calculate(self, *args):
        """Logic to perform the math and handle errors (Requirement 2)."""
        try:
            # Get raw input
            raw_bill = self.bill_amount.get()
            
            # If the box is empty, just reset the display
            if not raw_bill:
                self.result_label.config(text="Total per Person: $0.00")
                return

            # Convert to float for math
            bill = float(raw_bill)
            tip_val = self.tip_percent.get()
            diners = self.num_diners.get()

            # The Math
            total_tip = bill * (tip_val / 100)
            total_bill = bill + total_tip
            per_person = total_bill / diners

            # Update the UI
            self.result_label.config(text=f"Total per Person: ${per_person:.2f}")
            
        except ValueError:
            # This handles non-numeric entries gracefully
            self.result_label.config(text="Invalid Input", fg="red")

# --- Application Entry Point ---
if __name__ == "__main__":
    root = tk.Tk()
    app = TipCalculator(root)
    root.mainloop()