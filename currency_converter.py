import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class CurrencyConverter:
    """Currency Converter Application with GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # API Configuration
        self.api_key = "YOUR_API_KEY_HERE"  # Замените на ваш API ключ
        self.base_url = "https://v6.exchangerate-api.com/v6"
        
        # Available currencies
        self.currencies = self.get_supported_currencies()
        
        # History file
        self.history_file = "history.json"
        self.conversion_history = self.load_history()
        
        # Create GUI
        self.create_widgets()
        
        # Load currencies
        self.load_currency_list()
    
    def get_supported_currencies(self) -> Dict[str, str]:
        """Return dictionary of supported currencies"""
        return {
            "USD": "US Dollar",
            "EUR": "Euro",
            "GBP": "British Pound",
            "JPY": "Japanese Yen",
            "RUB": "Russian Ruble",
            "CNY": "Chinese Yuan",
            "INR": "Indian Rupee",
            "BRL": "Brazilian Real",
            "CAD": "Canadian Dollar",
            "AUD": "Australian Dollar",
            "CHF": "Swiss Franc",
            "KRW": "South Korean Won",
            "SEK": "Swedish Krona",
            "NOK": "Norwegian Krone",
            "MXN": "Mexican Peso"
        }
    
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Currency Converter", 
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # From Currency
        ttk.Label(main_frame, text="From:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.from_currency = ttk.Combobox(
            main_frame, 
            width=20, 
            state="readonly"
        )
        self.from_currency.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(0, 10))
        self.from_currency.current(0)  # Default to first currency
        
        # To Currency
        ttk.Label(main_frame, text="To:").grid(
            row=1, column=2, sticky=tk.W, pady=5
        )
        self.to_currency = ttk.Combobox(
            main_frame, 
            width=20, 
            state="readonly"
        )
        self.to_currency.grid(row=1, column=3, sticky=tk.W, pady=5)
        self.to_currency.current(1)  # Default to second currency
        
        # Amount
        ttk.Label(main_frame, text="Amount:").grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        self.amount_entry = ttk.Entry(main_frame, width=25)
        self.amount_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(0, 10))
        self.amount_entry.insert(0, "1.00")
        
        # Convert Button
        self.convert_btn = ttk.Button(
            main_frame, 
            text="Convert", 
            command=self.convert_currency,
            style='Accent.TButton'
        )
        self.convert_btn.grid(row=2, column=3, sticky=tk.W, pady=5)
        
        # Result
        self.result_frame = ttk.LabelFrame(main_frame, text="Result", padding="10")
        self.result_frame.grid(
            row=3, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=20
        )
        
        self.result_label = ttk.Label(
            self.result_frame, 
            text="", 
            font=('Arial', 14, 'bold')
        )
        self.result_label.grid(row=0, column=0)
        
        # Rate info
        self.rate_label = ttk.Label(
            self.result_frame, 
            text="", 
            font=('Arial', 10)
        )
        self.rate_label.grid(row=1, column=0, pady=(5, 0))
        
        # History section
        history_frame = ttk.LabelFrame(main_frame, text="Conversion History", padding="10")
        history_frame.grid(
            row=4, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0)
        )
        
        # History table
        columns = ('date', 'from_curr', 'to_curr', 'amount', 'result')
        self.history_tree = ttk.Treeview(
            history_frame, 
            columns=columns, 
            show='headings',
            height=8
        )
        
        # Define headings
        self.history_tree.heading('date', text='Date')
        self.history_tree.heading('from_curr', text='From')
        self.history_tree.heading('to_curr', text='To')
        self.history_tree.heading('amount', text='Amount')
        self.history_tree.heading('result', text='Result')
        
        # Define column widths
        self.history_tree.column('date', width=150)
        self.history_tree.column('from_curr', width=100)
        self.history_tree.column('to_curr', width=100)
        self.history_tree.column('amount', width=100)
        self.history_tree.column('result', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            history_frame, 
            orient=tk.VERTICAL, 
            command=self.history_tree.yview
        )
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid placement
        self.history_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # History buttons
        history_btn_frame = ttk.Frame(history_frame)
        history_btn_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(
            history_btn_frame, 
            text="Clear History", 
            command=self.clear_history
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            history_btn_frame, 
            text="Save History", 
            command=self.save_history
        ).pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_bar = ttk.Label(
            main_frame, 
            text="Ready", 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        self.status_bar.grid(
            row=5, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 0)
        )
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(3, weight=1)
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        
        # Load history
        self.update_history_table()
    
    def load_currency_list(self):
        """Load currencies into comboboxes"""
        currency_list = [f"{code} - {name}" for code, name in self.currencies.items()]
        self.from_currency['values'] = currency_list
        self.to_currency['values'] = currency_list
    
    def validate_amount(self, amount_str: str) -> Optional[float]:
        """Validate and convert amount string to float"""
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror(
                    "Error", 
                    "Amount must be a positive number!"
                )
                return None
            return amount
        except ValueError:
            messagebox.showerror(
                "Error", 
                "Please enter a valid number!"
            )
            return None
    
    def get_exchange_rate(self, from_curr: str, to_curr: str) -> Optional[float]:
        """Get exchange rate from API"""
        try:
            if self.api_key == "YOUR_API_KEY_HERE":
                # Demo mode - return sample rates if no API key
                messagebox.showwarning(
                    "Demo Mode",
                    "Using demo rates. Get your API key from exchangerate-api.com"
                )
                return self.get_demo_rate(from_curr, to_curr)
            
            # Make API request
            url = f"{self.base_url}/{self.api_key}/pair/{from_curr}/{to_curr}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['result'] == 'success':
                return data['conversion_rate']
            else:
                messagebox.showerror("API Error", "Failed to get exchange rate")
                return None
                
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Network Error", f"Failed to connect to API: {str(e)}")
            return None
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            return None
    
    def get_demo_rate(self, from_curr: str, to_curr: str) -> float:
        """Return demo exchange rates for testing"""
        # Sample rates (approximate)
        rates = {
            "USD": {"EUR": 0.85, "GBP": 0.73, "JPY": 110.0, "RUB": 75.0},
            "EUR": {"USD": 1.18, "GBP": 0.86, "JPY": 129.0, "RUB": 88.0},
            "GBP": {"USD": 1.37, "EUR": 1.16, "JPY": 150.0, "RUB": 102.0}
        }
        
        if from_curr in rates and to_curr in rates[from_curr]:
            return rates[from_curr][to_curr]
        elif from_curr == to_curr:
            return 1.0
        else:
            return 0.5  # Default dummy rate
    
    def convert_currency(self):
        """Perform currency conversion"""
        # Get selected currencies
        from_selection = self.from_currency.get()
        to_selection = self.to_currency.get()
        
        if not from_selection or not to_selection:
            messagebox.showwarning("Selection Error", "Please select both currencies")
            return
        
        # Extract currency codes
        from_curr = from_selection.split(" - ")[0]
        to_curr = to_selection.split(" - ")[0]
        
        # Validate amount
        amount = self.validate_amount(self.amount_entry.get())
        if amount is None:
            return
        
        # Get exchange rate
        self.status_bar.config(text="Fetching exchange rate...")
        self.root.update()
        
        rate = self.get_exchange_rate(from_curr, to_curr)
        
        if rate is not None:
            # Calculate result
            result = amount * rate
            
            # Display result
            self.result_label.config(
                text=f"{amount:.2f} {from_curr} = {result:.2f} {to_curr}"
            )
            self.rate_label.config(text=f"Exchange Rate: 1 {from_curr} = {rate:.4f} {to_curr}")
            
            # Add to history
            self.add_to_history(from_curr, to_curr, amount, result, rate)
            self.status_bar.config(text="Conversion completed successfully")
        else:
            self.status_bar.config(text="Conversion failed")
    
    def add_to_history(self, from_curr: str, to_curr: str, 
                      amount: float, result: float, rate: float):
        """Add conversion to history"""
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "from_currency": from_curr,
            "to_currency": to_curr,
            "amount": amount,
            "result": result,
            "rate": rate
        }
        
        self.conversion_history.append(entry)
        self.update_history_table()
        self.save_history()
    
    def update_history_table(self):
        """Update the history table"""
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Add history items (show last 20)
        for entry in self.conversion_history[-20:]:
            self.history_tree.insert('', 'end', values=(
                entry['date'],
                entry['from_currency'],
                entry['to_currency'],
                f"{entry['amount']:.2f}",
                f"{entry['result']:.2f}"
            ))
    
    def clear_history(self):
        """Clear conversion history"""
        if messagebox.askyesno("Clear History", 
                               "Are you sure you want to clear all history?"):
            self.conversion_history = []
            self.update_history_table()
            self.save_history()
            self.status_bar.config(text="History cleared")
    
    def save_history(self):
        """Save history to JSON file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversion_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save history: {str(e)}")
    
    def load_history(self) -> List[Dict]:
        """Load history from JSON file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

def main():
    """Main function to run the application"""
    root = tk.Tk()
    
    # Set style
    style = ttk.Style()
    style.theme_use('clam')  # Modern theme
    
    app = CurrencyConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()