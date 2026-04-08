import ttkbootstrap as tb  # The 'bootstrap' version of tkinter
from ttkbootstrap.constants import *

class TipCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Tip Calculator")
        self.root.geometry("400x550")
        
        # --- Variables ---
        # These hold the data and allow the 'trace' to monitor changes
        self.bill_amount = tb.StringVar(value="")
        self.tip_percent = tb.DoubleVar(value=15.0)
        self.num_diners = tb.IntVar(value=1)
        
        # Setup the UI
        self.setup_ui()
        
        # --- Requirement 5: Auto-Update Logic ---
        # Whenever these variables are 'written' to, run self.calculate
        self.bill_amount.trace_add("write", self.calculate)
        self.tip_percent.trace_add("write", self.calculate)
        self.num_diners.trace_add("write", self.calculate)

    def setup_ui(self):
        """Creates the layout using Bootstrap-styled widgets."""
        # Main container with padding
        main_frame = tb.Frame(self.root, padding=20)
        main_frame.pack(fill=BOTH, expand=YES)

        # 1. Bill Input (Requirement 2)
        tb.Label(main_frame, text="Bill Total ($)", font=("Helvetica", 10)).pack(pady=(10, 2))
        self.entry = tb.Entry(main_frame, textvariable=self.bill_amount, bootstyle="primary")
        self.entry.pack(fill=X, pady=5)

        # 2. Tip Percentage Slider (Requirement 3)
        # Using a slider allows any value, but we default it to 15%
        tb.Label(main_frame, text="Tip Percentage (%)", font=("Helvetica", 10)).pack(pady=(20, 2))
        self.tip_slider = tb.Scale(
            main_frame, 
            variable=self.tip_percent, 
            from_=0, 
            to=50, 
            bootstyle="info"
        )
        self.tip_slider.pack(fill=X, pady=5)
        
        # Label to show the current slider value
        self.tip_display = tb.Label(main_frame, text="15%", font=("Helvetica", 9, "italic"))
        self.tip_display.pack()

        # 3. Number of Diners (Requirement 4)
        tb.Label(main_frame, text="Number of Diners", font=("Helvetica", 10)).pack(pady=(20, 2))
        self.diner_spin = tb.Spinbox(
            main_frame, 
            from_=1, 
            to=50, 
            textvariable=self.num_diners, 
            bootstyle="primary"
        )
        self.diner_spin.pack(fill=X, pady=5)

        # 4. Results Area
        self.result_label = tb.Label(
            main_frame, 
            text="$0.00", 
            font=("Helvetica", 24, "bold"), 
            bootstyle="success"
        )
        self.result_label.pack(pady=40)
        tb.Label(main_frame, text="per person", font=("Helvetica", 10)).pack()

        # 5. Exit Button (Requirement 6)
        self.exit_btn = tb.Button(
            main_frame, 
            text="Exit", 
            bootstyle="danger-outline", 
            command=self.root.quit
        )
        self.exit_btn.pack(side=BOTTOM, pady=10)

    def calculate(self, *args):
        """The math engine that updates in real-time."""
        try:
            # Update the percentage text label
            self.tip_display.config(text=f"{int(self.tip_percent.get())}%")
            
            # Math logic
            bill = float(self.bill_amount.get()) if self.bill_amount.get() else 0.0
            tip = self.tip_percent.get() / 100
            diners = self.num_diners.get() if self.num_diners.get() > 0 else 1
            
            total_with_tip = bill * (1 + tip)
            per_person = total_with_tip / diners
            
            # Update Result (Requirement 5)
            self.result_label.config(text=f"${per_person:.2f}", bootstyle="success")
            
        except ValueError:
            # Handles non-numeric input (Requirement 2)
            self.result_label.config(text="Invalid Input", bootstyle="danger")

# --- Launch the App ---
if __name__ == "__main__":
    # We use tb.Window instead of tk.Tk for the bootstrap theme
    root = tb.Window(themename="flatly") 
    app = TipCalculator(root)
    root.mainloop()