import streamlit as st
import json
from block import Block
from transaction import Transaction
from miner import Blockchain

# Initialize session state
if 'blockchain' not in st.session_state:
    st.session_state.blockchain = Blockchain(roll_no="SYSTEM")
    
if 'accounts' not in st.session_state:
    st.session_state.accounts = {}  # Will store {account_name: {"balance": amount, "roll_no": roll_number}}
    
if 'pending_transactions' not in st.session_state:
    st.session_state.pending_transactions = []

def calculate_zakat(balance, rate=0.025):
    """Calculate zakat at 2.5% of balance"""
    return balance * rate

def apply_zakat_to_accounts():
    """Apply zakat to all accounts with balance > threshold"""
    zakat_threshold = 1000  # Minimum balance for zakat obligation
    zakat_collected = 0
    zakat_details = []
    
    for account_name in st.session_state.accounts:
        balance = st.session_state.accounts[account_name]["balance"]
        if balance >= zakat_threshold:
            zakat_amount = calculate_zakat(balance)
            st.session_state.accounts[account_name]["balance"] -= zakat_amount
            zakat_collected += zakat_amount
            roll_no = st.session_state.accounts[account_name]["roll_no"]
            zakat_details.append(f"{account_name} ({roll_no}): {zakat_amount:.2f}")
    
    return zakat_collected, zakat_details

class TransactionWrapper:
    """Wrapper for Transaction class to work with our account structure"""
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        
    def apply_to_accounts(self):
        """Apply transaction to our account structure"""
        if self.sender not in st.session_state.accounts or self.receiver not in st.session_state.accounts:
            raise Exception("Sender or receiver does not exist.")
            
        if st.session_state.accounts[self.sender]["balance"] < self.amount:
            raise Exception("Insufficient balance.")
            
        st.session_state.accounts[self.sender]["balance"] -= self.amount
        st.session_state.accounts[self.receiver]["balance"] += self.amount

def process_pending_transactions():
    """Process all pending transactions and create a new block"""
    if not st.session_state.pending_transactions:
        return False
    
    # Apply zakat before processing transactions
    zakat_collected, zakat_details = apply_zakat_to_accounts()
    
    # Create transaction records
    transaction_records = []
    successful_transactions = []
    
    # Add zakat collection record if any zakat was collected
    if zakat_collected > 0:
        transaction_records.append(f"Zakat Collection: {zakat_collected:.2f} collected")
        for detail in zakat_details:
            transaction_records.append(f"  Zakat from {detail}")
    
    for transaction in st.session_state.pending_transactions:
        try:
            # Apply transaction to accounts
            transaction.apply_to_accounts()
            sender_roll = st.session_state.accounts[transaction.sender]["roll_no"]
            receiver_roll = st.session_state.accounts[transaction.receiver]["roll_no"]
            transaction_records.append(f"{transaction.sender} ({sender_roll}) → {transaction.receiver} ({receiver_roll}): {transaction.amount}")
            successful_transactions.append(transaction)
        except Exception as e:
            st.error(f"Transaction failed: {e}")
            return False
    
    # Create new block with successful transactions
    if transaction_records:
        # Use the roll number of the first transaction sender as miner
        miner_roll = st.session_state.accounts[st.session_state.pending_transactions[0].sender]["roll_no"] if st.session_state.pending_transactions else "SYSTEM"
        block_success = st.session_state.blockchain.add_block(
            transactions=transaction_records,
            roll_no=miner_roll
        )
        
        if block_success:
            st.session_state.pending_transactions = []
            return True
    
    return False

# Streamlit UI
st.title("🔗 Mini Blockchain System")
st.markdown("---")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a page:", 
                           ["Account Management", "Transactions", "Blockchain View", "Validation"])

if page == "Account Management":
    st.header("💰 Account Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Create New Account")
        new_account = st.text_input("Account Name:")
        roll_number = st.text_input("Roll Number:")
        initial_balance = st.number_input("Initial Balance:", min_value=0.0, step=100.0)
        
        if st.button("Create Account"):
            if new_account and roll_number and new_account not in st.session_state.accounts:
                st.session_state.accounts[new_account] = {
                    "balance": initial_balance,
                    "roll_no": roll_number
                }
                st.success(f"Account '{new_account}' created for roll {roll_number} with balance: {initial_balance}")
            elif new_account in st.session_state.accounts:
                st.error("Account already exists!")
            else:
                st.error("Please enter valid account name and roll number.")
    
    with col2:
        st.subheader("Current Accounts")
        if st.session_state.accounts:
            for account, data in st.session_state.accounts.items():
                balance = data["balance"]
                roll_no = data["roll_no"]
                zakat_due = calculate_zakat(balance) if balance >= 1000 else 0
                
                st.write(f"**{account}** ({roll_no}): {balance:.2f}")
                if zakat_due > 0:
                    st.caption(f"   📊 Zakat due: {zakat_due:.2f}")
        else:
            st.info("No accounts created yet.")

elif page == "Transactions":
    st.header("💸 Transaction Management")
    
    if len(st.session_state.accounts) < 2:
        st.warning("You need at least 2 accounts to perform transactions.")
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Create Transaction")
            
            # Create account options with roll numbers
            account_options = [f"{name} ({data['roll_no']})" for name, data in st.session_state.accounts.items()]
            account_names = list(st.session_state.accounts.keys())
            
            sender_option = st.selectbox("From:", account_options)
            sender_idx = account_options.index(sender_option)
            sender = account_names[sender_idx]
            
            # Filter receiver options (exclude sender)
            receiver_options = [opt for i, opt in enumerate(account_options) if i != sender_idx]
            receiver_names = [name for i, name in enumerate(account_names) if i != sender_idx]
            
            receiver_option = st.selectbox("To:", receiver_options)
            receiver = receiver_names[receiver_options.index(receiver_option)]
            
            # Show current balance
            st.info(f"Sender balance: {st.session_state.accounts[sender]['balance']:.2f}")
            
            amount = st.number_input("Amount:", min_value=0.01, step=0.01)
            
            if st.button("Add to Pending"):
                if sender and receiver and amount > 0:
                    if st.session_state.accounts[sender]["balance"] >= amount:
                        new_transaction = TransactionWrapper(sender, receiver, amount)
                        st.session_state.pending_transactions.append(new_transaction)
                        sender_roll = st.session_state.accounts[sender]["roll_no"]
                        receiver_roll = st.session_state.accounts[receiver]["roll_no"]
                        st.success(f"Transaction added: {sender} ({sender_roll}) → {receiver} ({receiver_roll}): {amount}")
                    else:
                        st.error("Insufficient balance!")
                else:
                    st.error("Please fill all fields with valid values.")
        
        with col2:
            st.subheader("Pending Transactions")
            if st.session_state.pending_transactions:
                for i, tx in enumerate(st.session_state.pending_transactions, 1):
                    sender_roll = st.session_state.accounts[tx.sender]["roll_no"]
                    receiver_roll = st.session_state.accounts[tx.receiver]["roll_no"]
                    st.write(f"{i}. {tx.sender} ({sender_roll}) → {tx.receiver} ({receiver_roll}): {tx.amount}")
                
                if st.button("🔨 Mine Block", type="primary"):
                    if process_pending_transactions():
                        st.success("Block mined successfully! Zakat applied.")
                        st.rerun()
                    else:
                        st.error("Failed to mine block.")
            else:
                st.info("No pending transactions.")

elif page == "Blockchain View":
    st.header("⛓️ Blockchain Explorer")
    
    if st.session_state.blockchain.chain:
        st.subheader(f"Total Blocks: {len(st.session_state.blockchain.chain)}")
        
        # Display blocks in reverse order (newest first)
        for i, block in enumerate(reversed(st.session_state.blockchain.chain)):
            block_index = len(st.session_state.blockchain.chain) - i - 1
            
            with st.expander(f"Block #{block_index} - Mined by: {block.roll_no} - Hash: {block.hash[:16]}..."):
                st.write(f"**Timestamp:** {block.timestamp}")
                st.write(f"**Mined by Roll No:** {block.roll_no}")
                st.write(f"**Previous Hash:** {block.prev_hash}")
                st.write(f"**Current Hash:** {block.hash}")
                
                st.write("**Transactions:**")
                if isinstance(block.transactions, list):
                    for tx in block.transactions:
                        st.write(f"  • {tx}")
                else:
                    st.write(f"  • {block.transactions}")
    else:
        st.info("No blocks in the blockchain yet.")

elif page == "Validation":
    st.header("🔍 Blockchain Validation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Validate Blockchain", type="primary"):
            is_valid = st.session_state.blockchain.is_valid()
            
            if is_valid:
                st.success("✅ Blockchain is valid!")
            else:
                st.error("❌ Blockchain validation failed!")
    
    with col2:
        st.subheader("Chain Statistics")
        st.metric("Total Blocks", len(st.session_state.blockchain.chain))
        st.metric("Pending Transactions", len(st.session_state.pending_transactions))
        total_accounts = len(st.session_state.accounts)
        total_balance = sum(acc["balance"] for acc in st.session_state.accounts.values()) if st.session_state.accounts else 0
        st.metric("Total Accounts", total_accounts)
        st.metric("Total Balance", f"{total_balance:.2f}")

# Footer with system info
st.markdown("---")
st.markdown("### 📊 System Status")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Active Accounts", len(st.session_state.accounts))
with col2:
    st.metric("Blockchain Length", len(st.session_state.blockchain.chain))
with col3:
    st.metric("Pending Transactions", len(st.session_state.pending_transactions))

# Debug section (collapsible)
with st.expander("🔧 Debug Information"):
    st.write("**Current Accounts:**")
    if st.session_state.accounts:
        account_display = {}
        for name, data in st.session_state.accounts.items():
            account_display[name] = {
                "balance": data["balance"],
                "roll_no": data["roll_no"]
            }
        st.json(account_display)
    else:
        st.write("No accounts")
    
    st.write("**Pending Transactions:**")
    if st.session_state.pending_transactions:
        pending_tx_data = []
        for tx in st.session_state.pending_transactions:
            pending_tx_data.append({
                "sender": tx.sender,
                "receiver": tx.receiver,
                "amount": tx.amount,
                "sender_roll": st.session_state.accounts[tx.sender]["roll_no"],
                "receiver_roll": st.session_state.accounts[tx.receiver]["roll_no"]
            })
        st.json(pending_tx_data)
    else:
        st.write("None")

# Quick start guide
if len(st.session_state.accounts) == 0:
    st.info("""
    🚀 **Quick Start Guide:**
    1. Go to 'Account Management' to create accounts with roll numbers and initial balances
    2. Head to 'Transactions' to create and mine transactions
    3. Check 'Blockchain View' to see your mined blocks with roll number attribution
    4. Use 'Validation' to verify blockchain integrity
    """)