class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount

    def apply(self, accounts):
        """
        Apply the transaction to the accounts dictionary.
        Prevent transaction if sender has insufficient balance.
        """
        if self.sender not in accounts or self.receiver not in accounts:
            raise Exception("Sender or receiver does not exist.")

        if accounts[self.sender] < self.amount:
            raise Exception("Insufficient balance.")

        accounts[self.sender] -= self.amount
        accounts[self.receiver] += self.amount

        return accounts
