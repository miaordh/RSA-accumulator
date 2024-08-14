import main
import sys
import time
import merkletools
from helpfunctions import hash_to_prime, write_list_to_file, write_two_d_array_to_file, extract_merkle_proof, create_random_list, hash_integers, to_padded_num_str, make_even_size
from dotenv import dotenv_values


config = dotenv_values(".env")
RANDOM_LIST_SIZE = int(config["RANDOM_LIST_SIZE"])
RANDOM_LIST_MAXIMUM_LENGTH = int(config["RANDOM_LIST_MAXIMUM_LENGTH"])
SINGLE_PROVE_INDEX = int(config["SINGLE_PROVE_INDEX"])
BATCH_PROVE_SIZE = int(config["BATCH_PROVE_SIZE"])
sys.set_int_max_str_digits(10000000)

# Create random list
random_list = create_random_list(RANDOM_LIST_SIZE, RANDOM_LIST_MAXIMUM_LENGTH)
random_list_hashed = hash_integers(random_list) # Merkle tree needs hashed elements
# Convert the random list into hexadecimal numbers
random_list_hex = [] 
for num in random_list:
    num_hex = make_even_size(hex(num))
    random_list_hex.append(num_hex)
checked = random_list[SINGLE_PROVE_INDEX] # The element checked
write_list_to_file(random_list, './textlist/random_list.txt')
write_list_to_file(random_list_hashed, './textlist/random_list_hashed.txt')
write_list_to_file(random_list_hex, './textlist/random_list_hex.txt')
print("Random list size: {}".format(RANDOM_LIST_SIZE))
print("Later at the batch checking stage, we will batch check {} elements.".format(BATCH_PROVE_SIZE))

# Set up an RSA Accumulator
n, A0, S = main.setup()
n_hex = to_padded_num_str(n, 384)
A0_hex = make_even_size(hex(A0))
print("RSA Accumulator setup done")
with open("./textlist/n_hex.txt",'w') as n_hex_file:
    n_hex_file.write(n_hex)
with open("./textlist/A0_hex.txt",'w') as A0_hex_file:
    A0_hex_file.write(A0_hex)

# Adding to RSA Accumulator
startAdd = time.time()
A, _ = main.batch_add(A0, S, random_list, n)
stopAdd = time.time()
A_hex = to_padded_num_str(A, 384)
print("RSA Accumulator batch add done, which takes {} seconds".format(stopAdd - startAdd))
with open('./textlist/accumulated_A_hex.txt','w') as A_hex_file:
    A_hex_file.write(A_hex)


# Adding to Merkle tree
mt = merkletools.MerkleTools()
startAdd = time.time()
mt.add_leaf(random_list_hashed)
mt.make_tree()
stopAdd = time.time()
print("Merkle tree add leaves done, which takes {} seconds\n\n".format(stopAdd - startAdd))

# Merkle tree get root, get leaf and generate proof for element checked
mt_proof = mt.get_proof(SINGLE_PROVE_INDEX)
proof_sides, proof_hashes = extract_merkle_proof(mt_proof)
write_list_to_file(proof_sides, './textlist/proof_sides_{}.txt'.format(SINGLE_PROVE_INDEX))
write_list_to_file(proof_hashes, './textlist/proof_hashes_{}.txt'.format(SINGLE_PROVE_INDEX))
mt_root = mt.get_merkle_root()
print("Merkle Tree root: {}".format(mt_root))
with open('./textlist/merkle_root_hash.txt','w') as merkle_root_hash_file:
    merkle_root_hash_file.write('0x' + mt_root)

print("Checking single element with index {}. Extract random_list[{}]\n".format(SINGLE_PROVE_INDEX, SINGLE_PROVE_INDEX))
checked_leaf = mt.get_leaf(SINGLE_PROVE_INDEX)
mt_root = mt.get_merkle_root()

# RSA Accumulator prover generates proof
startProve = time.time()
A_proof = main.prove_membership(A0, S, checked, n)
stopProve = time.time()
A_proof_hex = to_padded_num_str(A_proof, 384)
nonce_verify = S[checked]

with open("./textlist/A_proof_hex.txt",'w') as A_proof_file:
    A_proof_file.write(A_proof_hex)
with open("./textlist/nonce_verify_hex.txt",'w') as nonce_verify_file:
    nonce_verify_file.write(hex(nonce_verify))
checked_hashed_to_prime = to_padded_num_str(hash_to_prime(checked, num_of_bits=128, nonce=nonce_verify)[0], 32)
with open("./textlist/element_{}_hashed_to_prime.txt".format(SINGLE_PROVE_INDEX),'w') as element_hashed_to_prime_file:
    element_hashed_to_prime_file.write(checked_hashed_to_prime)

# RSA Accumulator verifier verifies membership
startVerify = time.time()
membership = main.verify_membership(A, checked, nonce_verify, A_proof, n)
stopVerify = time.time()

print("Single element check. Using RSA Accumulator.\nMember? {}.\nGenerating proof takes {} seconds.\nVerifying takes {} seconds.\n".format(membership, stopProve - startProve, stopVerify - startVerify))

# Verifying membership using Python dictionary key search
tik = time.time()
simple_proof = random_list[SINGLE_PROVE_INDEX] in S
tok = time.time()

print("Single element check. Using Python dictionary key search.\nMember? {}.\nChecking takes {} seconds.\nWarning: Python dictionary key search is not a safe verification method.\n".format(simple_proof, tok - tik))

# Merkle tree verifying membership
startProve = time.time()
mt_proof = mt.get_proof(SINGLE_PROVE_INDEX)
stopProve = time.time()
startVerify = time.time()
mt_is_valid = mt.validate_proof(mt_proof, checked_leaf, mt_root)
stopVerify = time.time()
print("Single element check. Using Merkle tree validation.\nMember? {}.\nGenerating proof takes {} seconds.\nVerifying takes {} seconds.\n\n".format(mt_is_valid, stopProve - startProve, stopVerify - startVerify))

batch_checked = random_list[:BATCH_PROVE_SIZE]
# Now, checking elements with indices [0, BATCH_PROVE_SIZE - 1]
print("Now check a group of elements with indices [0, {}]\n".format(BATCH_PROVE_SIZE - 1))
startProve = time.time()
A_batch_proof = main.batch_prove_membership(A0, S, batch_checked, n)
stopProve = time.time()

with open("./textlist/A_batch_proof_hex.txt", 'w') as A_batch_proof_hex_file:
    A_batch_proof_hex_file.write(to_padded_num_str(A_batch_proof, 384))

batch_nonce = []
for key in batch_checked:
    batch_nonce.append(S[key])

batch_elements_hashed_to_prime = main.calculate_primes_product(batch_checked, batch_nonce)
with open("./textlist/batch_elements_hashed_to_prime.txt", 'w') as batch_elements_hashed_to_prime_file:
    batch_elements_hashed_to_prime_file.write(to_padded_num_str(batch_elements_hashed_to_prime, 32))


startVerify = time.time()
batch_membership = main.batch_verify_membership(A, batch_checked, batch_nonce, A_batch_proof, n)
stopVerify = time.time()
print("Batch check. Using RSA Accumulator.\nMember? {}.\nGenerating proof takes {} seconds ({} seconds per checked element).\nVerifying takes {} seconds ({} seconds per checked element).\n".format(batch_membership, stopProve - startProve, (stopProve - startProve)/BATCH_PROVE_SIZE, stopVerify - startVerify, (stopVerify - startVerify)/BATCH_PROVE_SIZE))

# Comparing with Python dictionary
batch_membership = True
tik = time.time()
for key in batch_checked:
    membership = key in S
    if membership == False:
        batch_membership = False
        break
tok = time.time()
print("Batch check. Using Python dictionary key search.\nMember? {}.\nChecking takes {} seconds ({} seconds per checked element).\n".format(batch_membership, tok - tik, (tok - tik)/BATCH_PROVE_SIZE))

# Comparing with Merkle Tree
membership = True
prove_time = 0.0
verify_time = 0.0
batch_mt_proof_hashes = []
batch_mt_proof_sides = []
for i in range(BATCH_PROVE_SIZE):
    tik = time.time()
    mt_proof = mt.get_proof(i)
    tok = time.time()
    prove_time += tok - tik
    proof_side, proof_hash = extract_merkle_proof(mt_proof)
    batch_mt_proof_hashes.append(proof_hash)
    batch_mt_proof_sides.append(proof_side)

    checked_leaf = mt.get_leaf(i)
    tik = time.time()
    mt_is_valid = mt.validate_proof(mt_proof, checked_leaf, mt_root)
    tok = time.time()
    verify_time += tok - tik
    if mt_is_valid == False:
        membership = False
        break

write_two_d_array_to_file(batch_mt_proof_hashes, "./textlist/batch_proof_hashes.txt")
write_two_d_array_to_file(batch_mt_proof_sides, "./textlist/batch_proof_sides.txt")

print("Batch check. Using Merkle tree validation.\nMember? {}.\nGenerating proof takes {} seconds ({} seconds per checked element).\nVerifying takes {} seconds ({} seconds per checked element).\n".format(membership, prove_time, prove_time / BATCH_PROVE_SIZE, verify_time, verify_time / BATCH_PROVE_SIZE))
