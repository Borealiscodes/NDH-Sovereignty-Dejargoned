import pytest
import numpy as np
from ndh_demo.transformer import TransformerBoundEngine

def test_attention_mimicry_dot_product_scaling():
    """Asserts that inner product matrix query-key tensors scale cleanly by 1/sqrt(80)."""
    bound_engine = TransformerBoundEngine(dimension=80)
    q = np.ones(80) * 0.5
    k = np.ones(80) * 0.5
    
    # Expected dot product: 80 * (0.5 * 0.5) = 20.0
    # Expected scaling factor: sqrt(80)
    expected_scalar = 20.0 / np.sqrt(80)
    calculated_scalar = bound_engine.calculate_attention_mimicry(q, k)
    
    assert np.isclose(calculated_scalar, expected_scalar, atol=1e-7)

def test_finite_time_capacity_exhaustion_trigger():
    """Models a predictable capacity cutoff sequence under continuous linear input load steps."""
    # Initialize engine with a low capacity ceiling to ensure immediate termination verification
    bound_engine = TransformerBoundEngine(dimension=80, capacity_ceiling=3.0)
    q = np.ones(80) * 2.0
    k = np.ones(80) * 2.0
    
    breached = False
    for _ in range(15):
        breached, current_drift = bound_engine.evaluate_capacity_step(q, k, drift_coeff=2.5)
        if breached:
            break
            
    assert breached is True
    assert current_drift >= 3.0
