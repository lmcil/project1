"""
Enhanced Expense Tracker Application
Features: Add, Edit, Delete, Sort, Summary with Average, and Pie Chart
Author: Senior Python Developer
"""

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os


class ExpenseTracker:
    """
    Manages expense tracking with full CRUD operations and analytics.
    """
    
    EXPENSE_FILE = 'expenses.csv'
    
    def __init__(self):
        """Initialize the expense tracker."""
        self.expenses_df = self._load_expenses()
    
    def _load_expenses(self):
        """
        Load expenses from CSV file or create empty DataFrame.
        
        Returns:
            pd.DataFrame: Expenses data
        """
        if os.path.exists(self.EXPENSE_FILE):
            try:
                df = pd.read_csv(self.EXPENSE_FILE)
                print(f"✓ Loaded {len(df)} expenses from file")
                return df
            except Exception as e:
                print(f"Error loading expenses: {e}")
                return self._create_empty_dataframe()
        else:
            print("No existing expenses found. Starting fresh.")
            return self._create_empty_dataframe()
    
    def _create_empty_dataframe(self):
        """Create an empty DataFrame with proper columns."""
        return pd.DataFrame(columns=['Date', 'Category', 'Description', 'Amount'])
    
    def _save_expenses(self):
        """Save expenses to CSV file, sorted by amount."""
        try:
            # Sort by amount before saving (requirement #3)
            sorted_df = self.expenses_df.sort_values(by='Amount', ascending=False)
            sorted_df.to_csv(self.EXPENSE_FILE, index=False)
            self.expenses_df = sorted_df
            print("✓ Expenses saved and sorted by amount")
        except Exception as e:
            print(f"✗ Error saving expenses: {e}")
    
    def add_expense(self):
        """Add a new expense to the tracker."""
        print("\n--- Add New Expense ---")
        
        try:
            category = input("Category (e.g., Food, Transport, Entertainment): ").strip()
            description = input("Description: ").strip()
            amount = float(input("Amount ($): "))
            
            if amount <= 0:
                print("✗ Amount must be greater than 0")
                return
            
            # Get current date/time
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Create new expense
            new_expense = pd.DataFrame({
                'Date': [current_datetime],
                'Category': [category],
                'Description': [description],
                'Amount': [amount]
            })
            
            # Add to DataFrame
            self.expenses_df = pd.concat([self.expenses_df, new_expense], ignore_index=True)
            self._save_expenses()
            
            print(f"✓ Expense added: ${amount:.2f} for {category}")
            
        except ValueError:
            print("✗ Invalid amount entered")
        except Exception as e:
            print(f"✗ Error adding expense: {e}")
    
    def edit_expense(self):
        """Edit an existing expense (requirement #1)."""
        print("\n--- Edit Expense ---")
        
        if self.expenses_df.empty:
            print("No expenses to edit")
            return
        
        # Display expenses with indices
        self._display_expenses_with_index()
        
        try:
            index = int(input("\nEnter expense index to edit: "))
            
            if index < 0 or index >= len(self.expenses_df):
                print("✗ Invalid index")
                return
            
            print(f"\nEditing expense at index {index}")
            print(f"Current: {self.expenses_df.iloc[index].to_dict()}")
            
            # Get new values
            category = input("New Category (press Enter to keep current): ").strip()
            description = input("New Description (press Enter to keep current): ").strip()
            amount_str = input("New Amount (press Enter to keep current): ").strip()
            
            # Update only if new values provided
            if category:
                self.expenses_df.at[index, 'Category'] = category
            if description:
                self.expenses_df.at[index, 'Description'] = description
            if amount_str:
                amount = float(amount_str)
                if amount <= 0:
                    print("✗ Amount must be greater than 0")
                    return
                self.expenses_df.at[index, 'Amount'] = amount
            
            # Automatically update date/time when edited (requirement #1)
            self.expenses_df.at[index, 'Date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self._save_expenses()
            print("✓ Expense updated successfully")
            
        except ValueError:
            print("✗ Invalid input")
        except Exception as e:
            print(f"✗ Error editing expense: {e}")
    
    def delete_expense(self):
        """Delete an expense by index (requirement #2)."""
        print("\n--- Delete Expense ---")
        
        if self.expenses_df.empty:
            print("No expenses to delete")
            return
        
        # Display expenses with indices
        self._display_expenses_with_index()
        
        try:
            index = int(input("\nEnter expense index to delete: "))
            
            if index < 0 or index >= len(self.expenses_df):
                print("✗ Invalid index")
                return
            
            # Show expense to be deleted
            expense_to_delete = self.expenses_df.iloc[index]
            print(f"\nDeleting: {expense_to_delete['Category']} - ${expense_to_delete['Amount']:.2f}")
            
            confirm = input("Are you sure? (yes/no): ").strip().lower()
            
            if confirm == 'yes':
                self.expenses_df = self.expenses_df.drop(index).reset_index(drop=True)
                self._save_expenses()
                print("✓ Expense deleted successfully")
            else:
                print("Deletion cancelled")
                
        except ValueError:
            print("✗ Invalid index entered")
        except Exception as e:
            print(f"✗ Error deleting expense: {e}")
    
    def _display_expenses_with_index(self):
        """Display all expenses with their indices."""
        print("\n{:<6} {:<20} {:<15} {:<30} {:<10}".format(
            "Index", "Date", "Category", "Description", "Amount"
        ))
        print("-" * 85)
        
        for idx, row in self.expenses_df.iterrows():
            print("{:<6} {:<20} {:<15} {:<30} ${:<9.2f}".format(
                idx,
                row['Date'],
                row['Category'],
                row['Description'][:28],
                row['Amount']
            ))
    
    def view_expenses(self):
        """Display all expenses."""
        print("\n--- All Expenses ---")
        
        if self.expenses_df.empty:
            print("No expenses recorded yet")
            return
        
        self._display_expenses_with_index()
        print(f"\nTotal Expenses: {len(self.expenses_df)}")
    
    def show_summary(self):
        """Display expense summary with average (requirement #4)."""
        print("\n--- Expense Summary ---")
        
        if self.expenses_df.empty:
            print("No expenses recorded yet")
            return
        
        # Calculate statistics
        total = self.expenses_df['Amount'].sum()
        average = self.expenses_df['Amount'].mean()  # Requirement #4
        max_expense = self.expenses_df['Amount'].max()
        min_expense = self.expenses_df['Amount'].min()
        count = len(self.expenses_df)
        
        # Summary by category
        category_summary = self.expenses_df.groupby('Category')['Amount'].agg(['sum', 'count'])
        
        print(f"\n{'='*50}")
        print(f"Total Expenses:   ${total:,.2f}")
        print(f"Average Expense:  ${average:,.2f}")  # Requirement #4
        print(f"Number of Items:  {count}")
        print(f"Highest Expense:  ${max_expense:,.2f}")
        print(f"Lowest Expense:   ${min_expense:,.2f}")
        print(f"{'='*50}\n")
        
        print("Expenses by Category:")
        print(f"{'Category':<20} {'Total':<15} {'Count':<10}")
        print("-" * 45)
        for category, row in category_summary.iterrows():
            print(f"{category:<20} ${row['sum']:<14,.2f} {int(row['count']):<10}")
    
    def generate_pie_chart(self):
        """Generate a pie chart of expenses by category (requirement #5)."""
        print("\n--- Generate Pie Chart ---")
        
        if self.expenses_df.empty:
            print("No expenses to chart")
            return
        
        try:
            # Group by category and sum amounts
            category_totals = self.expenses_df.groupby('Category')['Amount'].sum()
            
            # Create pie chart
            plt.figure(figsize=(10, 8))
            colors = plt.cm.Set3.colors
            
            wedges, texts, autotexts = plt.pie(
                category_totals,
                labels=category_totals.index,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors
            )
            
            # Enhance text properties
            for text in texts:
                text.set_fontsize(12)
                text.set_weight('bold')
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(10)
                autotext.set_weight('bold')
            
            plt.title('Expenses by Category', fontsize=16, weight='bold', pad=20)
            
            # Add legend with dollar amounts
            legend_labels = [f'{cat}: ${amt:.2f}' 
                           for cat, amt in category_totals.items()]
            plt.legend(legend_labels, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1))
            
            plt.axis('equal')
            plt.tight_layout()
            
            # Save chart
            chart_filename = 'expense_chart.png'
            plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
            print(f"✓ Pie chart saved as '{chart_filename}'")
            
            # Display chart
            plt.show()
            
        except Exception as e:
            print(f"✗ Error generating pie chart: {e}")
    
    def run(self):
        """Main application loop."""
        print("=" * 60)
        print("    EXPENSE TRACKER - Enhanced Edition")
        print("=" * 60)
        
        while True:
            print("\n" + "=" * 60)
            print("MENU:")
            print("1. Add Expense")
            print("2. View All Expenses")
            print("3. Edit Expense")
            print("4. Delete Expense")
            print("5. Show Summary (with Average)")
            print("6. Generate Pie Chart")
            print("7. Exit")
            print("=" * 60)
            
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == '1':
                self.add_expense()
            elif choice == '2':
                self.view_expenses()
            elif choice == '3':
                self.edit_expense()
            elif choice == '4':
                self.delete_expense()
            elif choice == '5':
                self.show_summary()
            elif choice == '6':
                self.generate_pie_chart()
            elif choice == '7':
                print("\n✓ Thank you for using Expense Tracker!")
                print("✓ All expenses saved to 'expenses.csv'")
                break
            else:
                print("✗ Invalid choice. Please enter 1-7")


def main():
    """Application entry point."""
    try:
        tracker = ExpenseTracker()
        tracker.run()
    except KeyboardInterrupt:
        print("\n\n✓ Application closed")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")


if __name__ == '__main__':
    main()