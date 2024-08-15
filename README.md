# RSA-accumulator
Original GitHub project by oleiba

Cryptographic accumulator based on the strong RSA assumption [Bd94, BP97, CL02, BBF18].<br>
Generating and verifying proofs in Python, verifier in Solidity.<br>

A Sepolia implementation of the original project.

### Dependencies assumed

* Python3
* python-dotenv
* NPM

### Unit testing

```
$ python3 -m unittest test
```

In test.py, hash_to_prime function outputs prime with 128-bit length, regardless of value set up in .env.

### Benchmarks

* Compare performance (compared with Python Merkle Tree [1]):
```
$ python3 test-performance.py
```

* The Python file `implementation.py` can also show performance.

### How to run the project

1. Check if you have all dependencies assumed. For ```python-dotenv```, you may install by running:
```
$ python3 -m pip install python-dotenv
```

2. Run the command to install the other dependencies:

```
$ npm install
```

3. Create an `.env` file according to `.env.example`. You may leave fields ```MerkleProof_ADDRESS``` and ```RSAAccumulator_ADDRESS``` empty now.

4. Run the Python file `implementation.py` to see performance. Meanwhile, ```implementation.py``` also generates necessary text files for smart contract deployment and interaction.

5. Run the following commands for compilation and deployment of contracts:

```
$ npx hardhat compile
$ npx hardhat run deployments/deploy.js --network sepolia
```
Copy the contract addresses into `.env` accordingly. You can find the contract addresses in the printouts that look like:

```
MerkleProof Contract Deployed to Address: 0x1234567890abcdef1234567890abcdef12345678
RSAAccumulator Contract Deployed to Address: 0x7890abcdef1234567890abcdef1234567890abcd
```



6. Run:

```
$ node interact.js
```


### References

[Bd94] [One-way accumulators: A decentralized
alternative to digital sinatures](https://link.springer.com/content/pdf/10.1007/3-540-48285-7_24.pdf), Josh Cohen Benaloh and Michael de Mare.<br> 
[BP97] [Collision-free accumulators and fail-stop signature
schemes without trees](https://link.springer.com/content/pdf/10.1007/3-540-69053-0_33.pdf), Niko Bari and Birgit Pfitzmann. <br>
[CL02] [Dynamic accumulators and application to
efficient revocation of anonymous credentials](https://link.springer.com/content/pdf/10.1007/3-540-45708-9_5.pdf), Jan Camenisch and Anna Lysyanskaya. <br>
[BBF18] [Batching Techniques for Accumulators with Applications to IOPs and Stateless Blockchains](~https://eprint.iacr.org/2018/1188.pdf~), Dan Boneh, Benedikt Bünz, Benjamin Fisch.<br>

