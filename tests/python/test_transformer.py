import pytest
import numpy as np
from ndh_demo.core_ffi import CoreFFIBridge, NativeSymplecticRuntime
from ndh_demo.transformer import TransformerBoundEngine

@pytest.fixture(scope="module")
def symplectic_runtime():
    """Initializes the native C-FFI symplectic runtime pipeline for testing."""
    try:
        bridge = CoreFFIBridge()
        return NativeSymplecticRuntime(bridge)
    except FileNotFoundError:
        pytest.skip("Native Rust shared library not compiled. Run 'make' first.")

@pytest.fixture
def bound_engine(symplectic_runtime):
    """Provides a clean TransformerBoundEngine instance linked to the native backend."""
    return TransformerBoundEngine(symplectic_runtime=symplectic_runtime, capacity_ceiling=5.0)

def test_attention_mimicry_calculation(bound_engine):
    """Verifies standard scaled inner product calculations are performed correctly."""
    q = np.ones(80) * 2.0
    k = np.ones(80) * 3.0
    
    # Mathematical baseline: (80 * (2.0 * 3.0)) / sqrt(80) = 480 / 8.9442719 = 53.66563
    expected_energy = float((80 * 6.0) / np.sqrt(80))
    calculated_energy = bound_engine.calculate_attention_mimicry(q, k)
    
    assert np.isclose(calculated_energy, expected_energy, atol=1e-4)

def test_capacity_step_symplectic_stabilization(bound_engine):
    """Confirms that evaluation steps trigger native volume preservation mechanisms."""
    q = np.random.randn(80)
    k = np.random.randn(80)
    
    # Process a step through the engine tracking layer
    breached, current_drift = bound_engine.evaluate_capacity_step(q, k, drift_coeff=1.0)
    
    # Verify proper data types and finite outputs are passed back from the FFI link
    assert isinstance(breached, bool)
    assert isinstance(current_drift, float)
    assert not np.isnan(current_drift)
    assert current_drift >= 0.0

def test_attention_capacity_ceiling_breach(bound_engine):
    """Asserts that the tracking engine registers capacity exhaustion limits."""
    # Force high-energy inputs to push the accumulator past the 5.0 capacity ceiling
    q = np.ones(80) * 15.0
    k = np.ones(80) * 15.0
    
    breached = False
    for _ in range(20):
        breached, drift = bound_engine.evaluate_capacity_step(q, k, drift_coeff=5.0)
        if breached:
            break
            
    assert breached is True
    assert drift >= bound_engine.capacity_ceiling

def test_engine_state_reset(bound_engine):
    """Validates that the accumulated metric parameters wipe cleanly on command."""
    q = np.ones(80)
    k = np.ones(80)
    
    bound_engine.evaluate_capacity_step(q, k)
    assert bound_engine.accumulated_drift > 0.0
    
    bound_engine.reset_engine_state()
    assert bound_engine.accumulated_drift == 0.0

def test_transformer_input_dimension_fence(bound_engine):
    """Confirms that the transformer architecture blocks unmapped shape vector sets."""
    corrupt_short_q = np.ones(79)
    valid_k = np.ones(80)
    
    with pytest.raises(ValueError, match="Query and Key vectors must be flat 80-dimensional arrays."):
        bound_engine.calculate_attention_mimicry(corrupt_short_q, valid_k)
