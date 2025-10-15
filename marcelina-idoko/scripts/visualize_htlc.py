"""
Visualizes HTLC execution flow
"""
import sys
sys.path.append('..')

from htlc_implementation import create_htlc_script, HTLCSimulator

def visualize_execution():
    """Show step-by-step execution"""
    print("\n" + "="*70)
    print(" HTLC EXECUTION VISUALIZATION")
    print("="*70)
    
    secret = "atomic_swap_secret"
    alice = "alice_pubkey"
    bob = "bob_pubkey"
    
    sim = HTLCSimulator(secret, alice, bob)
    
    print("\n📊 SCENARIO: Alice claims with secret at block 15")
    print("\nStack execution (Alice's path):")
    print("  1. Push signature        → Stack: [sig]")
    print("  2. Push public key       → Stack: [sig, pubkey]")
    print("  3. Push secret           → Stack: [sig, pubkey, secret]")
    print("  4. Push 1 (TRUE)         → Stack: [sig, pubkey, secret, 1]")
    print("  5. OP_IF (takes IF)      → Enters Alice's branch")
    print("  6. OP_SHA256             → Stack: [sig, pubkey, hash(secret)]")
    print("  7. Push expected hash    → Stack: [sig, pubkey, hash1, hash2]")
    print("  8. OP_EQUALVERIFY        → Verifies & removes → [sig, pubkey]")
    print("  9. OP_DUP                → Stack: [sig, pubkey, pubkey]")
    print(" 10. OP_HASH160            → Stack: [sig, pubkey, hash160(pubkey)]")
    print(" 11. Push Alice's hash     → Stack: [sig, pubkey, hash1, hash2]")
    print(" 12. OP_EQUALVERIFY        → Verifies & removes → [sig, pubkey]")
    print(" 13. OP_CHECKSIG           → Verifies signature → [1]")
    print(" 14. Result: SUCCESS ✓")
    
    print("\n" + "="*70)
    print("\n📊 SCENARIO: Bob refunds at block 25")
    print("\nStack execution (Bob's path):")
    print("  1. Push signature        → Stack: [sig]")
    print("  2. Push public key       → Stack: [sig, pubkey]")
    print("  3. Push 0 (FALSE)        → Stack: [sig, pubkey, 0]")
    print("  4. OP_IF (takes ELSE)    → Enters Bob's branch")
    print("  5. Push timeout (21)     → Stack: [sig, pubkey, 21]")
    print("  6. OP_CHECKLOCKTIMEVERIFY → Verifies block 25 >= 21 ✓")
    print("  7. OP_DROP               → Stack: [sig, pubkey]")
    print("  8. OP_DUP                → Stack: [sig, pubkey, pubkey]")
    print("  9. OP_HASH160            → Stack: [sig, pubkey, hash160(pubkey)]")
    print(" 10. Push Bob's hash       → Stack: [sig, pubkey, hash1, hash2]")
    print(" 11. OP_EQUALVERIFY        → Verifies & removes → [sig, pubkey]")
    print(" 12. OP_CHECKSIG           → Verifies signature → [1]")
    print(" 13. Result: SUCCESS ✓")

if __name__ == "__main__":
    visualize_execution()
