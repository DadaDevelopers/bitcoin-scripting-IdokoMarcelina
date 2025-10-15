import sys
sys.path.append('..')

from htlc_implementation import HTLCSimulator

def test_alice_valid_claim():
    """Test Alice claiming with correct secret"""
    secret = "test_secret_123"
    alice_key = "alice_key"
    bob_key = "bob_key"
    
    sim = HTLCSimulator(secret, alice_key, bob_key)
    result = sim.validate_alice_claim(secret, alice_key, 10)
    
    assert result == True, "Alice's valid claim should succeed"
    print("✓ Test passed: Alice valid claim")

def test_alice_invalid_secret():
    """Test Alice claiming with wrong secret"""
    secret = "test_secret_123"
    alice_key = "alice_key"
    bob_key = "bob_key"
    
    sim = HTLCSimulator(secret, alice_key, bob_key)
    result = sim.validate_alice_claim("wrong_secret", alice_key, 10)
    
    assert result == False, "Alice's invalid claim should fail"
    print("✓ Test passed: Alice invalid secret")

def test_bob_refund_before_timeout():
    """Test Bob refund before timeout"""
    secret = "test_secret_123"
    alice_key = "alice_key"
    bob_key = "bob_key"
    
    sim = HTLCSimulator(secret, alice_key, bob_key)
    result = sim.validate_bob_refund(bob_key, 10, 21)
    
    assert result == False, "Bob's refund before timeout should fail"
    print("✓ Test passed: Bob refund blocked before timeout")

def test_bob_refund_after_timeout():
    """Test Bob refund after timeout"""
    secret = "test_secret_123"
    alice_key = "alice_key"
    bob_key = "bob_key"
    
    sim = HTLCSimulator(secret, alice_key, bob_key)
    result = sim.validate_bob_refund(bob_key, 25, 21)
    
    assert result == True, "Bob's refund after timeout should succeed"
    print("✓ Test passed: Bob refund after timeout")

if __name__ == "__main__":
    print("\nRunning HTLC Unit Tests...\n")
    test_alice_valid_claim()
    test_alice_invalid_secret()
    test_bob_refund_before_timeout()
    test_bob_refund_after_timeout()
    print("\n✓ All tests passed!\n")
