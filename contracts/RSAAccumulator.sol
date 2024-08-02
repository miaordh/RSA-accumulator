pragma solidity ^0.5.0;


contract RSAAccumulator {


    bytes acc_post;
    bytes modulus;


    constructor (bytes memory _modulus, bytes memory _acc_post) public {
        modulus = _modulus;
        acc_post = _acc_post;
    }

    event Result(bool success);

    function equal(bytes memory _preBytes, bytes memory _postBytes) internal pure returns (bool) {
        bool success = true;

        assembly {
            let length := mload(_preBytes)

        // if lengths don't match the arrays are not equal
            switch eq(length, mload(_postBytes))
            case 1 {
            // cb is a circuit breaker in the for loop since there's
            //  no said feature for inline assembly loops
            // cb = 1 - don't breaker
            // cb = 0 - break
                let cb := 1

                let mc := add(_preBytes, 0x20)
                let end := add(mc, length)

                for {
                    let cc := add(_postBytes, 0x20)
                // the next line is the loop condition:
                // while(uint(mc < end) + cb == 2)
                } eq(add(lt(mc, end), cb), 2) {
                    mc := add(mc, 0x20)
                    cc := add(cc, 0x20)
                } {
                // if any of these checks fails then arrays are not equal
                    if iszero(eq(mload(mc), mload(cc))) {
                    // unsuccess:
                        success := 0
                        cb := 0
                    }
                }
            }
            default {
            // unsuccess:
                success := 0
            }
        }

        return success;
    }

    function verify(bytes memory base, bytes32 e) public returns (bool) {
        // Count the loops required for base (blocks of 32 bytes)
        uint base_length = base.length;
        uint loops_base = (base_length + 31) / 32;
        // Count the loops required for modulus (blocks of 32 bytes)
        uint modulus_length = modulus.length;
        uint loops_modulus = (modulus_length + 31) / 32;
        bytes memory _modulus = modulus;

        bytes memory p;
        // are all of these inside the precompile now?
        assembly {
        // define pointer
            p := mload(0x40)
        // store data assembly-favouring ways
            mstore(p, base_length)

            mstore(add(p, 0x20), 0x180)  // Length of Base
            mstore(add(p, 0x40), 0x20)  // Length of Exponent
            mstore(add(p, 0x60), 0x180)  // Length of Modulus

            for { let i := 0 } lt(i, loops_base) { i := add(1, i) } { mstore(add(add(p, 0x80), mul(32, i)), mload(add(base, mul(32, add(i, 1))))) }  // Base

            mstore(add(p, 0x200), e)  // Exponent

        // Add the contents of b to the array
            for { let i := 0 } lt(i, loops_modulus) { i := add(1, i) } { mstore(add(add(p, 0x220), mul(32, i)), mload(add(_modulus, mul(32, add(i, 1))))) }  // Modulus

        // call modexp precompile!
            let success := call(sub(gas, 2000), 0x05, 0, add(p, 0x20), 0x380, add(p, 0x20), 0x180)

        // gas fiddling
            switch success case 0 {
                revert(0, 0)
            }
        // data
            mstore(0x40, add(p, add(0x20, base_length)))
        // o := p
        }
        emit Result(equal(p, acc_post));
        return equal(p, acc_post);
    }
}
