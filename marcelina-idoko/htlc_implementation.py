"""
Bitcoin HTLC (Hashed Time-Lock Contract) Implementation
For atomic swap between Alice and Bob

Requirements:
- Alice can claim with secret preimage within 21 minutes
- Bob gets refund after 21 minutes
"""

import hashlib
import time

# ============================================================================
# HTLC SCRIPT STRUCTURE
# ============================================================================

def create_htlc_script(secret_hash, alice_pubkey_hash, bob_pubkey_hash, timeout_blocks):
    """
    Creates an HTLC script with two spending paths:
    1. Alice's path (with secret) - available anytime before timeout
    2. Bob's refund path - available only after timeout
    
    Args:
        secret_hash: SHA256 hash of the secret
        alice_pubkey_hash: Alice's public key hash (HASH160)
        bob_pubkey_hash: Bob's public key hash (HASH160)
        timeout_blocks: Number of blocks for timeout (21 minutes ≈ 21 blocks)
    """
    
    script = f"""
# HTLC Script with Two Conditional Paths
# ============================================

OP_IF
    # Alice's claiming path (with secret preimage)
    # Requires: <signature> <pubkey> <secret> 1
    OP_SHA256                    # Hash the secret
    <{secret_hash}>              # Push expected secret hash
    OP_EQUALVERIFY               # Verify secret matches
    OP_DUP                       # Duplicate Alice's pubkey
    OP_HASH160                   # Hash it
    <{alice_pubkey_hash}>        # Push Alice's pubkey hash
    OP_EQUALVERIFY               # Verify pubkey matches
    OP_CHECKSIG                  # Verify signature
OP_ELSE
    # Bob's refund path (after timeout)
    # Requires: <signature> <pubkey> 0
    <{timeout_blocks}>           # Push timeout value
    OP_CHECKLOCKTIMEVERIFY       # Verify timeout has passed
    OP_DROP                      # Remove timeout from stack
    OP_DUP                       # Duplicate Bob's pubkey
    OP_HASH160                   # Hash it
    <{bob_pubkey_hash}>          # Push Bob's pubkey hash
    OP_EQUALVERIFY               # Verify pubkey matches
    OP_CHECKSIG                  # Verify signature
OP_ENDIF
"""
    return script


# ============================================================================
# CLAIMING TRANSACTION SCRIPT (Alice's Path)
# ============================================================================

def create_alice_claiming_script(signature, alice_pubkey, secret_preimage):
    """
    Alice's scriptSig to claim funds using the secret
    
    Args:
        signature: Alice's signature
        alice_pubkey: Alice's public key
        secret_preimage: The secret that hashes to the secret_hash
    
    Returns:
        scriptSig that unlocks the HTLC for Alice
    """
    
    script_sig = f"""
# Alice's Claiming Script (scriptSig)
# ====================================
<{signature}>          # Alice's signature
<{alice_pubkey}>       # Alice's public key
<{secret_preimage}>    # The secret preimage
1                      # OP_TRUE - takes the IF branch
"""
    return script_sig


# ============================================================================
# REFUND TRANSACTION SCRIPT (Bob's Path)
# ============================================================================

def create_bob_refund_script(signature, bob_pubkey):
    """
    Bob's scriptSig to claim refund after timeout
    
    Args:
        signature: Bob's signature
        bob_pubkey: Bob's public key
    
    Returns:
        scriptSig that unlocks the HTLC for Bob after timeout
    """
    
    script_sig = f"""
# Bob's Refund Script (scriptSig)
# =================================
<{signature}>          # Bob's signature
<{bob_pubkey}>         # Bob's public key
0                      # OP_FALSE - takes the ELSE branch
"""
    return script_sig


# ============================================================================
# EXECUTION SIMULATOR
# ============================================================================

class HTLCSimulator:
    """Simulates HTLC execution and validation"""
    
    def __init__(self, secret, alice_pubkey, bob_pubkey):
        self.secret = secret
        self.secret_hash = hashlib.sha256(secret.encode()).hexdigest()
        self.alice_pubkey = alice_pubkey
        self.bob_pubkey = bob_pubkey
        self.alice_pubkey_hash = self.hash160(alice_pubkey)
        self.bob_pubkey_hash = self.hash160(bob_pubkey)
        self.current_block = 0
        
    @staticmethod
    def hash160(data):
        """Simulates HASH160 (SHA256 + RIPEMD160)"""
        sha256_hash = hashlib.sha256(data.encode()).digest()
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha256_hash)
        return ripemd160.hexdigest()
    
    def validate_alice_claim(self, provided_secret, provided_pubkey, block_height):
        """Validates Alice's claim with secret"""
        print("\n" + "="*60)
        print("VALIDATING ALICE'S CLAIM")
        print("="*60)
        
        # Check secret
        provided_hash = hashlib.sha256(provided_secret.encode()).hexdigest()
        secret_valid = provided_hash == self.secret_hash
        print(f"Secret Hash Match: {secret_valid}")
        print(f"  Expected: {self.secret_hash}")
        print(f"  Provided: {provided_hash}")
        
        # Check pubkey
        pubkey_valid = provided_pubkey == self.alice_pubkey
        pubkey_hash_valid = self.hash160(provided_pubkey) == self.alice_pubkey_hash
        print(f"\nPublic Key Match: {pubkey_valid}")
        print(f"Public Key Hash Match: {pubkey_hash_valid}")
        
        # No timeout check for Alice's path
        print(f"\nBlock Height: {block_height} (no timeout restriction for Alice)")
        
        success = secret_valid and pubkey_hash_valid
        print(f"\n{'✓ CLAIM SUCCESSFUL' if success else '✗ CLAIM FAILED'}")
        print("="*60)
        
        return success
    
    def validate_bob_refund(self, provided_pubkey, block_height, timeout_blocks):
        """Validates Bob's refund after timeout"""
        print("\n" + "="*60)
        print("VALIDATING BOB'S REFUND")
        print("="*60)
        
        # Check timeout
        timeout_passed = block_height >= timeout_blocks
        print(f"Timeout Check: {timeout_passed}")
        print(f"  Current Block: {block_height}")
        print(f"  Timeout Block: {timeout_blocks}")
        print(f"  Status: {'PASSED' if timeout_passed else 'NOT YET'}")
        
        # Check pubkey
        pubkey_valid = provided_pubkey == self.bob_pubkey
        pubkey_hash_valid = self.hash160(provided_pubkey) == self.bob_pubkey_hash
        print(f"\nPublic Key Match: {pubkey_valid}")
        print(f"Public Key Hash Match: {pubkey_hash_valid}")
        
        success = timeout_passed and pubkey_hash_valid
        print(f"\n{'✓ REFUND SUCCESSFUL' if success else '✗ REFUND FAILED'}")
        print("="*60)
        
        return success


# ============================================================================
# TEST SUITE
# ============================================================================

def run_tests():
    """Test the HTLC implementation with various scenarios"""
    
    print("\n" + "="*70)
    print(" HTLC TEST SUITE - ATOMIC SWAP SIMULATION")
    print("="*70)
    
    # Setup
    secret = "super_secret_preimage_12345"
    alice_pubkey = "alice_public_key_xyz"
    bob_pubkey = "bob_public_key_abc"
    timeout_blocks = 21  # 21 minutes ≈ 21 blocks (10 min/block average)
    
    simulator = HTLCSimulator(secret, alice_pubkey, bob_pubkey)
    
    print("\n📋 SETUP PARAMETERS:")
    print(f"Secret: {secret}")
    print(f"Secret Hash: {simulator.secret_hash}")
    print(f"Alice PubKey Hash: {simulator.alice_pubkey_hash}")
    print(f"Bob PubKey Hash: {simulator.bob_pubkey_hash}")
    print(f"Timeout: {timeout_blocks} blocks (~21 minutes)")
    
    # Generate scripts
    print("\n" + "="*70)
    print(" GENERATED SCRIPTS")
    print("="*70)
    
    htlc_script = create_htlc_script(
        simulator.secret_hash,
        simulator.alice_pubkey_hash,
        simulator.bob_pubkey_hash,
        timeout_blocks
    )
    print("\n1. HTLC LOCKING SCRIPT (scriptPubKey):")
    print(htlc_script)
    
    alice_script = create_alice_claiming_script(
        "alice_signature_data",
        alice_pubkey,
        secret
    )
    print("\n2. ALICE'S CLAIMING SCRIPT (scriptSig):")
    print(alice_script)
    
    bob_script = create_bob_refund_script(
        "bob_signature_data",
        bob_pubkey
    )
    print("\n3. BOB'S REFUND SCRIPT (scriptSig):")
    print(bob_script)
    
    # Test scenarios
    print("\n" + "="*70)
    print(" TEST SCENARIOS")
    print("="*70)
    
    # Test 1: Alice claims with correct secret (block 10)
    print("\n\n🧪 TEST 1: Alice claims with correct secret at block 10")
    simulator.validate_alice_claim(secret, alice_pubkey, 10)
    
    # Test 2: Alice tries with wrong secret (block 10)
    print("\n\n🧪 TEST 2: Alice tries with wrong secret at block 10")
    simulator.validate_alice_claim("wrong_secret", alice_pubkey, 10)
    
    # Test 3: Bob tries refund before timeout (block 15)
    print("\n\n🧪 TEST 3: Bob tries refund before timeout at block 15")
    simulator.validate_bob_refund(bob_pubkey, 15, timeout_blocks)
    
    # Test 4: Bob claims refund after timeout (block 25)
    print("\n\n🧪 TEST 4: Bob successfully claims refund at block 25")
    simulator.validate_bob_refund(bob_pubkey, 25, timeout_blocks)
    
    # Test 5: Alice can still claim after timeout (block 25)
    print("\n\n🧪 TEST 5: Alice claims after timeout (still valid with secret)")
    simulator.validate_alice_claim(secret, alice_pubkey, 25)
    
    print("\n" + "="*70)
    print(" ATOMIC SWAP FLOW EXPLANATION")
    print("="*70)
    print("""
TYPICAL ATOMIC SWAP SEQUENCE:
1. Alice creates secret S and computes H(S)
2. Alice creates HTLC on Bitcoin with H(S), locks funds
3. Bob creates HTLC on another chain with same H(S), locks funds
4. Alice claims Bob's funds by revealing S
5. Bob sees S on blockchain, uses it to claim Alice's funds
6. If Alice doesn't reveal S, both can refund after timeout

SECURITY PROPERTIES:
✓ Atomicity: Either both swaps succeed or both fail
✓ Trustless: No trusted third party needed
✓ Time-bound: Clear timeout for refunds
✓ Secret-based: Only Alice initially knows the secret
    """)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    run_tests()