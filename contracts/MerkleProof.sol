pragma solidity ^0.5.0;

contract MerkleProof {
    // Function to check if a Merkle proof is valid


    function checkProof(
        bytes32[] memory proof, // Merkle proof (array of SHA256 hashes)
        bytes32 root, // Merkle root (SHA256 hash)
        bytes32 leaf, // Leaf to be verified (SHA256 hash)
        uint8[] memory sides // Array of 0s and 1s indicating sibling position (0 = left, 1 = right)
    ) public pure returns (bool) {
        bytes32 computedHash = leaf;

        // Iterate over each proof element
        for (uint256 i = 0; i < proof.length; i++) {
            bytes32 proofElement = proof[i];
            uint8 side = sides[i];

            // Check if the proof element is on the left or right
            if (side == 0) {
                // Combine the computed hash with the proof element (left)
                computedHash = sha256(abi.encodePacked(proofElement, computedHash));
            } else {
                // Combine the proof element with the computed hash (right)
                computedHash = sha256(abi.encodePacked(computedHash, proofElement));
            }
        }

        // Check if the computed hash matches the Merkle root
        return computedHash == root;
        
    }
}
