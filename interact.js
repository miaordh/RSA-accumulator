require('dotenv').config();
const fs = require('fs');

const PRIVATE_KEY = process.env.PRIVATE_KEY;
const API_KEY = process.env.API_KEY;
const MerkleProof_ADDRESS = process.env.MerkleProof_ADDRESS;
const RSAAccumulator_ADDRESS = process.env.RSAAccumulator_ADDRESS;



const SINGLE_PROVE_INDEX = process.env.SINGLE_PROVE_INDEX;
const gasLimit = 10000000;


const merkle_proof_contract = require("./artifacts/contracts/MerkleProof.sol/MerkleProof.json");
console.log('merkle_proof_contract found.')
const rsa_accumulator_contract = require("./artifacts/contracts/RSAAccumulator.sol/RSAAccumulator.json");
console.log('rsa_accumulator_contract_found.')


const ethers = require('ethers');

// Provider
const infuraProvider = new ethers.providers.InfuraProvider(
    "sepolia",
    API_KEY,
  );


// Signer
const signer = new ethers.Wallet(PRIVATE_KEY, infuraProvider);

// Contract

const MerkleProofContract = new ethers.Contract(MerkleProof_ADDRESS, merkle_proof_contract.abi, signer);
const RSAAccumulatorContract = new ethers.Contract(RSAAccumulator_ADDRESS, rsa_accumulator_contract.abi, signer);



// MerkleProof

const merkle_proof = fs.readFileSync(`./textlist/proof_hashes_${SINGLE_PROVE_INDEX}.txt`).toString().split('\n');
const elements_hashed = fs.readFileSync('./textlist/random_list_hashed.txt').toString().split('\n');
const element_hashed = '0x' + elements_hashed[SINGLE_PROVE_INDEX];
const merkle_root = fs.readFileSync('./textlist/merkle_root_hash.txt').toString();
const sides = fs.readFileSync(`./textlist/proof_sides_${SINGLE_PROVE_INDEX}.txt`).toString().split('\n');

// RSAAccumulator

const A_proof = fs.readFileSync(`./textlist/A_proof_hex.txt`).toString();
const element_hashed_to_prime = fs.readFileSync(`./textlist/element_${SINGLE_PROVE_INDEX}_hashed_to_prime.txt`).toString();


const batch_elements_hashed_to_prime = fs.readFileSync(`./textlist/batch_elements_hashed_to_prime.txt`).toString();
const A_batch_proof = fs.readFileSync(`./textlist/A_batch_proof_hex.txt`).toString();

async function validMerkleProof() {
  try {
    let gasEstimateRaw = await MerkleProofContract.estimateGas.checkProof(merkle_proof, merkle_root, element_hashed, sides);
    let gasEstimate = parseInt(gasEstimateRaw._hex, 16);
    console.log(`Merkle Proof - Estimated gas used: ${gasEstimate}`);
    let validity = await MerkleProofContract.checkProof(merkle_proof, merkle_root, element_hashed, sides);
    console.log(`Merkle Proof - Membership: ${validity}`);
    
  } catch (error) {
    console.error("Error calling contract method:", error);
  }
}
    
async function verifyRSAAccumulator() {
  try {
    let gasEstimateRaw = await RSAAccumulatorContract.estimateGas.verify(A_proof, element_hashed_to_prime, {gasLimit});
    let gasEstimate = parseInt(gasEstimateRaw._hex, 16);
    console.log(`Single element RSA Accumulator - Estimated gas used: ${gasEstimate}`);
    
    RSAAccumulatorContract.on(
      'Result', success => {
        console.log(`Single element RSA Accumulator - Membership: ${success}`);
        RSAAccumulatorContract.removeAllListeners('Result');
      }
    );
    let success = await RSAAccumulatorContract.verify(A_proof, element_hashed_to_prime, {gasLimit});

  } catch (error) {
    console.error("Error calling contract method:", error);
  }
}



async function batchVerifyRSAAccumulator() {
  try {
    let gasEstimateRaw = await RSAAccumulatorContract.estimateGas.verify(A_batch_proof, batch_elements_hashed_to_prime, {gasLimit});
    let gasEstimate = parseInt(gasEstimateRaw._hex, 16);
    console.log(`Batch RSA Accumulator - Estimated gas used: ${gasEstimate}`);
    
    RSAAccumulatorContract.on(
      'Result', success => {
        console.log(`Batch RSA Accumulator - Membership: ${success}`);
        RSAAccumulatorContract.removeAllListeners('Result');
      }
    );
    let success = await RSAAccumulatorContract.verify(A_batch_proof, batch_elements_hashed_to_prime, {gasLimit});

  } catch (error) {
    console.error("Error calling contract method:", error);
  }
}
validMerkleProof();
verifyRSAAccumulator();
// batchVerifyRSAAccumulator();
