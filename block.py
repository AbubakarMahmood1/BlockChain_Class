import hashlib, time

class Block:
    def __init__(self, transactions, prev_hash, roll_no):
        self.transactions = transactions
        self.timestamp = time.time()
        self.roll_no = roll_no
        self.prev_hash = prev_hash
        self.hash = self.compute_hash()   # Generate hash immediately

    def compute_hash(self):
        """
        Compute SHA-256 hash of block contents
        """
        block_string = str(self.transactions) + str(self.timestamp) + str(self.roll_no) + str(self.prev_hash)
        return hashlib.sha256(block_string.encode()).hexdigest()
