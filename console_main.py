from block import Block
from transaction import Transaction
from miner import Blockchain
import json
import os
import time

class BlockchainConsole:
    def __init__(self):
        self.blockchain = Blockchain(roll_no="SYSTEM")
        self.accounts = {}  # Will store {account_name: {"balance": amount, "roll_no": roll_number}}
        self.pending_transactions = []
        
    def clear_screen(self):
        """Clear console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def display_banner(self):
        """Display app banner"""
        print("=" * 60)
        print("          🔗 MINI BLOCKCHAIN SYSTEM 🔗")
        print("=" * 60)
        print()
        
    def calculate_zakat(self, balance, rate=0.025):
        """Calculate zakat at 2.5% of balance"""
        return balance * rate
        
    def apply_zakat_to_accounts(self):
        """Apply zakat to all accounts with balance > threshold"""
        zakat_threshold = 100
        zakat_collected = 0
        zakat_details = []
        
        for account_name in self.accounts:
            balance = self.accounts[account_name]["balance"]
            if balance >= zakat_threshold:
                zakat_amount = self.calculate_zakat(balance)
                self.accounts[account_name]["balance"] -= zakat_amount
                zakat_collected += zakat_amount
                roll_no = self.accounts[account_name]["roll_no"]
                zakat_details.append(f"{account_name} ({roll_no}): {zakat_amount:.2f}")
        
        return zakat_collected, zakat_details
        
    def create_account(self):
        """Create a new account"""
        print("\n--- CREATE ACCOUNT ---")
        account_name = input("Enter account name: ").strip()
        
        if not account_name:
            print("❌ Account name cannot be empty!")
            return
            
        if account_name in self.accounts:
            print("❌ Account already exists!")
            return
        
        roll_no = input("Enter roll number for this account: ").strip()
        if not roll_no:
            print("❌ Roll number cannot be empty!")
            return
            
        try:
            initial_balance = float(input("Enter initial balance: "))
            if initial_balance < 0:
                print("❌ Balance cannot be negative!")
                return
                
            self.accounts[account_name] = {
                "balance": initial_balance,
                "roll_no": roll_no
            }
            print(f"✅ Account '{account_name}' created for roll {roll_no} with balance: {initial_balance}")
            
        except ValueError:
            print("❌ Invalid balance amount!")
            
    def view_accounts(self):
        """Display all accounts and their balances"""
        print("\n--- ACCOUNT BALANCES ---")
        
        if not self.accounts:
            print("No accounts found.")
            return
            
        print(f"{'Account':<20} {'Roll No':<12} {'Balance':<15} {'Zakat Due':<12}")
        print("-" * 62)
        
        total_balance = 0
        total_zakat = 0
        
        for account_name, account_data in self.accounts.items():
            balance = account_data["balance"]
            roll_no = account_data["roll_no"]
            zakat_due = self.calculate_zakat(balance) if balance >= 1000 else 0
            total_balance += balance
            total_zakat += zakat_due
            
            zakat_str = f"{zakat_due:.2f}" if zakat_due > 0 else "N/A"
            print(f"{account_name:<20} {roll_no:<12} {balance:<15.2f} {zakat_str:<12}")
            
        print("-" * 62)
        print(f"{'TOTAL':<33} {total_balance:<15.2f} {total_zakat:<12.2f}")
        
    def create_transaction(self):
        """Create a new transaction"""
        print("\n--- CREATE TRANSACTION ---")
        
        if len(self.accounts) < 2:
            print("❌ Need at least 2 accounts to create transactions!")
            return
            
        print("Available accounts:")
        accounts_list = list(self.accounts.keys())
        for i, account in enumerate(accounts_list, 1):
            balance = self.accounts[account]["balance"]
            roll_no = self.accounts[account]["roll_no"]
            print(f"{i}. {account} ({roll_no}) - Balance: {balance:.2f}")
            
        try:
            sender_idx = int(input("Select sender account (number): ")) - 1
            receiver_idx = int(input("Select receiver account (number): ")) - 1
            
            if sender_idx < 0 or sender_idx >= len(accounts_list):
                print("❌ Invalid sender selection!")
                return
                
            if receiver_idx < 0 or receiver_idx >= len(accounts_list):
                print("❌ Invalid receiver selection!")
                return
                
            if sender_idx == receiver_idx:
                print("❌ Sender and receiver cannot be the same!")
                return
                
            sender = accounts_list[sender_idx]
            receiver = accounts_list[receiver_idx]
            
            amount = float(input("Enter amount: "))
            
            if amount <= 0:
                print("❌ Amount must be positive!")
                return
                
            if self.accounts[sender]["balance"] < amount:
                print("❌ Insufficient balance!")
                return
                
            # Create modified transaction that works with our account structure
            new_transaction = TransactionWrapper(sender, receiver, amount, self.accounts)
            self.pending_transactions.append(new_transaction)
            
            sender_roll = self.accounts[sender]["roll_no"]
            receiver_roll = self.accounts[receiver]["roll_no"]
            print(f"✅ Transaction added: {sender} ({sender_roll}) → {receiver} ({receiver_roll}): {amount}")
            
        except (ValueError, IndexError):
            print("❌ Invalid input!")
            
    def view_pending_transactions(self):
        """Display pending transactions"""
        print("\n--- PENDING TRANSACTIONS ---")
        
        if not self.pending_transactions:
            print("No pending transactions.")
            return
            
        for i, tx in enumerate(self.pending_transactions, 1):
            sender_roll = self.accounts[tx.sender]["roll_no"]
            receiver_roll = self.accounts[tx.receiver]["roll_no"]
            print(f"{i}. {tx.sender} ({sender_roll}) → {tx.receiver} ({receiver_roll}): {tx.amount}")
            
    def mine_block(self):
        """Mine a new block with pending transactions"""
        print("\n--- MINE BLOCK ---")
        
        if not self.pending_transactions:
            print("❌ No pending transactions to mine!")
            return
            
        print("Mining block...")
        time.sleep(1)  # Simulate mining time
        
        # Apply zakat before processing transactions
        zakat_collected, zakat_details = self.apply_zakat_to_accounts()
        
        # Create transaction records
        transaction_records = []
        successful_transactions = []
        
        # Add zakat collection record if any zakat was collected
        if zakat_collected > 0:
            transaction_records.append(f"Zakat Collection: {zakat_collected:.2f} collected")
            print(f"💰 Zakat collected: {zakat_collected:.2f}")
            for detail in zakat_details:
                print(f"   - {detail}")
        
        # Process each transaction
        for transaction in self.pending_transactions:
            try:
                # Apply transaction to accounts
                transaction.apply_to_accounts()
                sender_roll = self.accounts[transaction.sender]["roll_no"]
                receiver_roll = self.accounts[transaction.receiver]["roll_no"]
                transaction_records.append(f"{transaction.sender} ({sender_roll}) → {transaction.receiver} ({receiver_roll}): {transaction.amount}")
                successful_transactions.append(transaction)
                
            except Exception as e:
                print(f"❌ Transaction failed: {e}")
                return False
        
        # Create new block with successful transactions
        if transaction_records:
            # Use the roll number of the person mining (could be first transaction sender or system)
            miner_roll = self.accounts[self.pending_transactions[0].sender]["roll_no"] if self.pending_transactions else "SYSTEM"
            block_success = self.blockchain.add_block(
                transactions=transaction_records,
                roll_no=miner_roll
            )
            
            if block_success:
                self.pending_transactions = []
                print(f"✅ Block mined successfully by {miner_roll}!")
                print(f"   Block hash: {self.blockchain.chain[-1].hash}")
                print(f"   Transactions processed: {len(successful_transactions)}")
                return True
                
        print("❌ Failed to mine block!")
        return False
        
    def view_blockchain(self):
        """Display the entire blockchain"""
        print("\n--- BLOCKCHAIN EXPLORER ---")
        
        if not self.blockchain.chain:
            print("No blocks in blockchain.")
            return
            
        print(f"Total blocks: {len(self.blockchain.chain)}")
        print()
        
        for i, block in enumerate(self.blockchain.chain):
            print(f"📦 BLOCK #{i}")
            print(f"   Hash: {block.hash}")
            print(f"   Previous Hash: {block.prev_hash}")
            print(f"   Timestamp: {time.ctime(block.timestamp)}")
            print(f"   Mined by Roll No: {block.roll_no}")
            print("   Transactions:")
            
            if isinstance(block.transactions, list):
                for tx in block.transactions:
                    print(f"      • {tx}")
            else:
                print(f"      • {block.transactions}")
            print()
            
    def validate_blockchain(self):
        """Validate the blockchain integrity"""
        print("\n--- BLOCKCHAIN VALIDATION ---")
        
        print("Validating blockchain...")
        time.sleep(0.5)  # Simulate validation time
        
        is_valid = self.blockchain.is_valid()
        
        if is_valid:
            print("✅ Blockchain is VALID!")
            print("   All hashes are correct")
            print("   All links are intact")
        else:
            print("❌ Blockchain validation FAILED!")
            print("   Chain integrity compromised")
            
        return is_valid
        
    def display_menu(self):
        """Display the main menu"""
        print("\n" + "=" * 40)
        print("           MAIN MENU")
        print("=" * 40)
        print("1. Create Account")
        print("2. View Accounts")
        print("3. Create Transaction")
        print("4. View Pending Transactions")
        print("5. Mine Block")
        print("6. View Blockchain")
        print("7. Validate Blockchain")
        print("8. System Statistics")
        print("9. Exit")
        print("=" * 40)
        
    def display_statistics(self):
        """Display system statistics"""
        print("\n--- SYSTEM STATISTICS ---")
        print(f"Total Accounts: {len(self.accounts)}")
        print(f"Total Blocks: {len(self.blockchain.chain)}")
        print(f"Pending Transactions: {len(self.pending_transactions)}")
        
        if self.accounts:
            total_balance = sum(acc["balance"] for acc in self.accounts.values())
            total_zakat_due = sum(self.calculate_zakat(acc["balance"]) for acc in self.accounts.values() if acc["balance"] >= 1000)
            print(f"Total System Balance: {total_balance:.2f}")
            print(f"Total Zakat Due: {total_zakat_due:.2f}")
            
            # Show roll numbers
            print("\nRoll Numbers in System:")
            for name, data in self.accounts.items():
                print(f"  {name}: {data['roll_no']}")
            
        # Blockchain stats
        if len(self.blockchain.chain) > 1:
            latest_block = self.blockchain.chain[-1]
            print(f"Latest Block Hash: {latest_block.hash[:16]}...")
            print(f"Latest Block Time: {time.ctime(latest_block.timestamp)}")
            print(f"Latest Block Miner: {latest_block.roll_no}")
            
    def run(self):
        """Main application loop"""
        while True:
            self.clear_screen()
            self.display_banner()
            self.display_menu()
            
            try:
                choice = input("\nEnter your choice (1-9): ").strip()
                
                if choice == "1":
                    self.create_account()
                elif choice == "2":
                    self.view_accounts()
                elif choice == "3":
                    self.create_transaction()
                elif choice == "4":
                    self.view_pending_transactions()
                elif choice == "5":
                    self.mine_block()
                elif choice == "6":
                    self.view_blockchain()
                elif choice == "7":
                    self.validate_blockchain()
                elif choice == "8":
                    self.display_statistics()
                elif choice == "9":
                    print("\n👋 Thank you for using Mini Blockchain System!")
                    break
                else:
                    print("❌ Invalid choice! Please enter 1-9.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Exiting... Thank you for using Mini Blockchain System!")
                break
            except Exception as e:
                print(f"❌ An error occurred: {e}")
                
            input("\nPress Enter to continue...")


class TransactionWrapper:
    """Wrapper for Transaction class to work with our account structure"""
    def __init__(self, sender, receiver, amount, accounts_ref):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.accounts_ref = accounts_ref
        
    def apply_to_accounts(self):
        """Apply transaction to our account structure"""
        if self.sender not in self.accounts_ref or self.receiver not in self.accounts_ref:
            raise Exception("Sender or receiver does not exist.")
            
        if self.accounts_ref[self.sender]["balance"] < self.amount:
            raise Exception("Insufficient balance.")
            
        self.accounts_ref[self.sender]["balance"] -= self.amount
        self.accounts_ref[self.receiver]["balance"] += self.amount


if __name__ == "__main__":
    app = BlockchainConsole()
    app.run()