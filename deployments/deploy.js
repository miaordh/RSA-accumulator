

async function main() {
    const fs = require('fs');
    
    const n = fs.readFileSync("./textlist/n_hex.txt").toString();
    const acc_post = fs.readFileSync("./textlist/accumulated_A_hex.txt").toString();

    const MerkleProof = await ethers.getContractFactory("MerkleProof");
    const merkle_proof = await MerkleProof.deploy();
    console.log("MerkleProof Contract Deployed to Address:", merkle_proof.address);

    const RSAAccumulator = await ethers.getContractFactory("RSAAccumulator");
    
    const rsa_accumulator = await RSAAccumulator.deploy(n, acc_post);
    console.log("RSAAccumulator Contract Deployed to Address:", rsa_accumulator.address);
    
}

main()
  .then(() => process.exit(0))
  .catch(error => {
    console.error(error);
    process.exit(1);
  });