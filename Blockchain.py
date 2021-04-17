import json
from flask import Flask, jsonify, request
import pprint
from time import time
from random import randint
from hashlib import sha256

N_BITS_DIFFICULTY=4
DIFFICULTY=2**N_BITS_DIFFICULTY

class Block:
    def __init__(self, index, timestamp, transactions, proof, prev_hash):
        self.index=index 
        self.timestamp=timestamp
        self.transactions=transactions 
        self.proof=proof 
        self.prev_hash=prev_hash
    
    def as_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "proof": self.proof,
            "prev_hash": self.prev_hash
        }

    def hash(self):
        return sha256(
            json.dumps(
                self.as_dict(),
                sort_keys=True
            ).encode('utf8')
        ).hexdigest()
    
    def __str__(self):
        return pprint.pformat(self.as_dict(), indent=4)

class Blockchain:
    def __init__(self):
        self.chain=[
            Block(1, time(), [], randint(0,1000), randint(0,1000))
        ]
        self.pending_transactions=[]

    def addBlock(self, proof):
        self.chain.append(
            Block(
                len(self.chain)+1,
                time(),
                self.pending_transactions,
                proof,
                self.chain[-1].hash()
            )
        )
        self.pending_transactions=[]

    def isAppendable(self, new_block):
        return valid_proof(self.lastProof(), new_block.proof)

    def addTransaction(self, amount, sender, recipient):
        self.pending_transactions.append({
            "amount": amount,
            "sender": sender,
            "recipient": recipient
        })
        return len(self.chain)+1
    
    def validProof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:N_BITS_DIFFICULTY] == "0"*N_BITS_DIFFICULTY
    
    def lastBlock(self):
        return self.chain[-1]
    
    def lastProof(self):
        return self.lastBlock().proof
    
    def show(self):
        print("### My Blockchain Contents ###")
        print()
        print("Genesis Block:")
        print(self.chain[0])
        print()
        for n, block in enumerate(self.chain[1:]):
            print(f"Block {n+1}:")
            print(block)
            print()

if __name__=="__main__":

    b=Blockchain()

    # Instantiate our Node
    app = Flask(__name__)

    # Instantiate the Blockchain
    blockchain = Blockchain()

    @app.route('/lastblock', methods=['GET'])
    def lastBlock():
        lastblock=b.lastBlock()
        return jsonify(
            b.lastBlock().as_dict()
        ), 200

    @app.route('/difficulty', methods=['GET'])
    def difficulty():
        return jsonify(
            {
                "difficulty":DIFFICULTY,
            }
        ), 200

    @app.route('/transactions', methods=['GET'])
    def get_transactions():
        return jsonify(b.pending_transactions), 200

    @app.route('/transactions', methods=['POST'])
    def add_transaction():
        transaction = request.get_json()
        required = ['sender', 'recipient', 'amount']
        if not all(k in transaction for k in required):
            return 'Missing values', 400
        else:
            b.addTransaction(
                transaction['amount'], transaction['sender'], transaction['recipient']
            )
            return "Successfully added", 201

    @app.route('/addblock', methods=['POST'])
    def addBlock():
        pass

    app.run(host='0.0.0.0', port=5000)

