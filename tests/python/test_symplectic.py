import pytest
import numpy as np
from ndh_demo.core_ffi import CoreFFIBridge, NativeSymplecticRuntime

@pytest.fixture(scope="module")
def symplectic_runtime():
    """Initializes the native C-FFI pipeline bridge for the Symplectic Engine."""
    try:
        bridge = CoreFFIBridge()
        return NativeSymplecticRuntime(bridge)
    except FileNotFoundError:
        pytest.skip("Native Rust shared object binary is not compiled. Run 'make' first.")

def test_symplectic_load_and_export_identity(symplectic_runtime):
    """
    Verifies that loading an 80D state vector and exporting it immediately
    acts as a perfect geometric identity map (lossless conservation).
    """
    np.random.seed(1337)
    # Generate a random, unconstrained 80D coordinate array representing text/latent tokens
    mock_input_state = np.random.randn(80).astype(np.float64)
    
    # Load the state vector into the native heap-allocated struct
    symplectic_runtime.load_state(mock_input_state)
    
    # Immediately pull the state back out through the export pointer buffer
    exported_state = symplectic_runtime.export_state()
    
    # Assert that the data vector survived the FFI transmission boundary with zero error
    assert np.allclose(mock_input_state, exported_state, rtol=1e-12, atol=1e-12)

def test_symplectic_canonical_partition_integrity(symplectic_runtime):
    """
    Validates that the 80D array is precisely divided into independent 40D 
    position (q) and momentum (p) vector sub-spaces.
    """
    # Create an array where the first 40 entries are 1.0 (q) and the last 40 are 2.0 (p)
    structured_input = np.zeros(80, dtype=np.float64)
    structured_input[0:40] = 1.0
    structured_input[40:80] = 2.0
    
    symplectic_runtime.load_state(structured_input)
    exported_output = symplectic_runtime.export_state()
    
    # Verify index mapping integrity remains aligned and unmixed
    assert np.all(exported_output[0:40] == 1.0)
    assert np.all(exported_output[40:80] == 2.0)

def test_symplectic_invalid_dimension_rejection(symplectic_runtime):
    """
    Ensures that the Python validation guard blocks arrays that violate 
    the exact 80D geometric constraint before passing to native pointers.
    """
    invalid_short_array = np.ones(40, dtype=np.float64)
    
    with pytest.raises(ValueError, match="State vector must be a flat 1D array of exactly 80 elements."):
        symplectic_runtime.load_state(invalid_short_array)
