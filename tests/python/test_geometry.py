import pytest
import numpy as np
from ndh_demo.core_ffi import CoreFFIBridge, NativeManifoldRuntime

@pytest.fixture(scope="module")
def runtime():
    """Initializes the native C-FFI pipeline bridge for integration testing."""
    try:
        bridge = CoreFFIBridge()
        return NativeManifoldRuntime(bridge)
    except FileNotFoundError:
        pytest.skip("Native Rust shared object binary is not compiled. Run 'make' first.")

def test_metric_index_symmetry_invariant(runtime):
    """Verifies that the metric tensor update steps produce mathematically valid stability traces."""
    np.random.seed(42)
    mock_perturbation = np.random.randn(80) * 2.5
    
    # Execute metric evolution update step via Rust FFI
    trace_scalar = runtime.update_metric(mock_perturbation)
    
    # Assert that the structural transposition averaging returns a non-zero, finite trace value
    assert isinstance(trace_scalar, float)
    assert trace_scalar > 0.0
    assert not np.isnan(trace_scalar)

def test_9d_radial_laplacian_singularity_isolation(runtime):
    """Asserts that the 9D radial Laplacian operator safely uses its epsilon boundary near r=0."""
    # Pass a flat 0.0 radius which traditional un-isolated physics engines would crash on
    zero_radius_output = runtime.compute_9d_radial_laplacian(r=0.0, f_prime=1.5, f_double_prime=2.0)
    
    # Mathematical invariant baseline: 2.0 + (8.0 / 1e-12) * 1.5 = 12000000000002.0
    expected_baseline = 2.0 + (8.0 / 1e-12) * 1.5
    
    assert np.isclose(zero_radius_output, expected_baseline, atol=1e-2)
    assert not np.isnan(zero_radius_output)

def test_apex_gradient_normalization(runtime):
    """Validates that the apex gradient calculation enforces strict Euclidean vector scaling."""
    np.random.seed(123)
    arbitrary_gradient = np.random.randn(80) * 10.0
    
    normalized_vector = runtime.compute_apex_gradient(arbitrary_gradient)
    
    # Compute the magnitude of the returned vector state: ||x||
    vector_magnitude = np.sqrt(np.sum(normalized_vector ** 2))
    
    # The output must be a unit vector (norm == 1.0)
    assert np.isclose(vector_magnitude, 1.0, atol=1e-7)

def test_apex_gradient_underflow_isolation(runtime):
    """Verifies that vector norms below the EPSILON ceiling smoothly fallback to clean zero vectors."""
    near_zero_gradient = np.ones(80) * 1e-15
    
    fallback_vector = runtime.compute_apex_gradient(near_zero_gradient)
    
    # Underflow boundary must map directly to an evaluation state of absolute zero
    assert np.all(fallback_vector == 0.0)

def test_type_validator_nan_rejection(runtime):
    """Confirms that the native typeck validation layer safely rejects corrupt NaN data packets."""
    corrupt_vector = np.zeros(80)
    corrupt_vector[12] = np.nan
    
    with pytest.raises(ValueError, match="Native execution failed: Invariant array validation bounds error."):
        runtime.update_metric(corrupt_vector)

def test_type_validator_bounds_rejection(runtime):
    """Asserts that the native runtime blocks arrays that violate the exact 80D constraint."""
    invalid_short_vector = np.ones(79)
    
    with pytest.raises(ValueError, match="Perturbation vector must be a flat 1D array of exactly 80 elements."):
        runtime.update_metric(invalid_short_vector)
