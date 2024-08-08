# RSA-accumulator
Original GitHub project by oleiba

Cryptographic accumulator based on the strong RSA assumption [Bd94, BP97, CL02, BBF18].<br>
Generating and verifying proofs in Python, verifier in Solidity.<br>

A Sepolia implementation of the original project.

### Prerequesites

* Python3
* python-dotenv
* Node.js 20.15.1, NPM
* hardhat 2.22.6, NPM
* ethers 5.7.2, NPM
* @nomiclabs/hardhat-ethers 2.2.3, NPM
* dotenv 16.4.5, NPM

### Unit testing

`$ python3 -m unittest test`

### Benchmarks

* Compare performance (compared with Python Merkle Tree [1]):
```
$ python3 test-performance.py
```

* The Python file `implementation.py` can also show performance.

### How to run the project

Download all dependencies first.

Create an `.env` file according to `.env.example`

Copy all contents in `hardhat.config.js.example.txt` to replace hardhat.config.js before compilation.

Build an empty directory called `textlist`.

Run the Python file `implementation.py` to see performance and generate necessary text lists for smart contract deployment and interaction.

Run the following commands:

```
$ npx hardhat compile
$ npx hardhat run deployments/deploy.js --network sepolia
```

Copy contract addresses into `.env`

Run:

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
[BBF18] [Batching Techniques for Accumulators with Applications to IOPs and Stateless Blockchains](https://eprint.iacr.org/2018/1188.pdf), Dan Boneh, Benedikt Bünz, Benjamin Fisch.<br>
