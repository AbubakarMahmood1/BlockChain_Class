from block import Block

class Blockchain:
    def __init__(self, roll_no="0000"):
        self.chain = []
        self.create_genesis_block(roll_no)

    def create_genesis_block(self, roll_no):
        """
        Create the first block (genesis block)
        """
        genesis_block = Block(transactions="Genesis Block", prev_hash="0", roll_no=roll_no)
        self.chain.append(genesis_block)

    def add_block(self, transactions, roll_no):
        """
        Add a block to the chain after verifying previous hash
        """
        prev_block = self.chain[-1]
        new_block = Block(transactions=transactions, prev_hash=prev_block.hash, roll_no=roll_no)

        if new_block.prev_hash == prev_block.hash:
            self.chain.append(new_block)
            return True
        return False

    def is_valid(self):
        """
        Validate the blockchain by checking hashes
        """
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i - 1]

            if current.prev_hash != prev.hash:
                return False
            if current.hash != current.compute_hash():
                return False
        return True
