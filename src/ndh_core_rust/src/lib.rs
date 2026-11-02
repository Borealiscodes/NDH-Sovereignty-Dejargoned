pub mod manifold;
pub mod typeck;
pub mod codegen;
pub mod symplectic;

use manifold::ManifoldEngine80D;
use typeck::DataPacketValidator;
use symplectic::SymplecticEngine;

// =========================================================================
// Manifold Engine FFI Bindings
// =========================================================================

/// Opaque wrapper to manage the Rust manifold engine across runtime environments
#[no_mangle]
pub extern "C" fn create_manifold_engine() -> *mut ManifoldEngine80D {
    Box::into_raw(Box::new(ManifoldEngine80D::new()))
}

/// Frees the engine memory safely from the heap
#[no_mangle]
pub extern "C" fn free_manifold_engine(ptr: *mut ManifoldEngine80D) {
    if !ptr.is_null() {
        unsafe {
            let _ = Box::from_raw(ptr);
        }
    }
}

/// Exposed C-FFI binding to safely execute metric evolution steps from Python
#[no_mangle]
pub extern "C" fn execute_metric_evolution(
    engine_ptr: *mut ManifoldEngine80D,
    perturbation_ptr: *const f64,
    len: usize,
    out_stability_scalar: *mut f64,
) -> i32 {
    if engine_ptr.is_null() || perturbation_ptr.is_null() || out_stability_scalar.is_null() {
        return -1; // Null pointer guard condition triggered
    }

    // Convert the raw pointer slice safely
    let raw_slice = unsafe { std::slice::from_raw_parts(perturbation_ptr, len) };

    // Run type validation to guard against NaN/Inf values or bounding errors
    match DataPacketValidator::validate_array_bounds(raw_slice) {
        Ok(sanitized_array) => {
            let engine = unsafe { &mut *engine_ptr };
            let scalar = engine.update_metric_evolution(&sanitized_array);
            unsafe {
                *out_stability_scalar = scalar;
            }
            0 // Execution success code
        }
        Err(_) => -2, // Invariant validation failure code
    }
}

/// Native FFI hook executing Lean-verified apex gradient vector calculations
#[no_mangle]
pub extern "C" fn execute_compute_apex_gradient(
    engine_ptr: *const ManifoldEngine80D,
    gradient_in_ptr: *const f64,
    len: usize,
    vector_out_ptr: *mut f64,
) -> i32 {
    if engine_ptr.is_null() || gradient_in_ptr.is_null() || vector_out_ptr.is_null() || len != 80 {
        return -1;
    }

    let raw_slice = unsafe { std::slice::from_raw_parts(gradient_in_ptr, len) };
    match DataPacketValidator::validate_array_bounds(raw_slice) {
        Ok(sanitized_array) => {
            let engine = unsafe { &*engine_ptr };
            let normalized = engine.compute_apex_gradient(&sanitized_array);
            unsafe {
                std::ptr::copy_nonoverlapping(normalized.as_ptr(), vector_out_ptr, 80);
            }
            0
        }
        Err(_) => -2,
    }
}

/// Native FFI hook executing Lean-verified 9D radial Laplacian calculations
#[no_mangle]
pub extern "C" fn execute_compute_9d_radial_laplacian(
    engine_ptr: *const ManifoldEngine80D,
    r: f64,
    f_prime: f64,
    f_double_prime: f64,
    out_laplacian: *mut f64,
) -> i32 {
    if engine_ptr.is_null() || out_laplacian.is_null() {
        return -1;
    }
    
    let engine = unsafe { &*engine_ptr };
    let result = engine.compute_9d_radial_laplacian(r, f_prime, f_double_prime);
    unsafe {
        *out_laplacian = result;
    }
    0
}

// =========================================================================
// Symplectic Engine FFI Bindings
// =========================================================================

/// Allocates a new volume-preserving SymplecticEngine on the heap and returns a raw pointer
#[no_mangle]
pub extern "C" fn create_symplectic_engine() -> *mut SymplecticEngine {
    Box::into_raw(Box::new(SymplecticEngine::new()))
}

/// Safely drops and reclaims the heap memory allocated for a SymplecticEngine instance
#[no_mangle]
pub extern "C" fn free_symplectic_engine(ptr: *mut SymplecticEngine) {
    if !ptr.is_null() {
        unsafe {
            let _ = Box::from_raw(ptr);
        }
    }
}

/// Feeds an 80D state vector through our FFI boundary to partition coordinate pairs
#[no_mangle]
pub extern "C" fn load_symplectic_state(engine_ptr: *mut SymplecticEngine, state_ptr: *const f64, len: usize) -> i32 {
    if engine_ptr.is_null() || state_ptr.is_null() {
        return -1;
    }

    let raw_slice = unsafe { std::slice::from_raw_parts(state_ptr, len) };
    match DataPacketValidator::validate_array_bounds(raw_slice) {
        Ok(sanitized_array) => {
            let engine = unsafe { &mut *engine_ptr };
            engine.load_state(&sanitized_array);
            0
        }
        Err(_) => -2,
    }
}

/// Pulls back the processed canonical pairs and exports them out as an unconstrained 80D output block
#[no_mangle]
pub extern "C" fn export_symplectic_state(engine_ptr: *const SymplecticEngine, out_ptr: *mut f64, len: usize) -> i32 {
    if engine_ptr.is_null() || out_ptr.is_null() || len != 80 {
        return -1;
    }

    let engine = unsafe { &*engine_ptr };
    let exported = engine.export_state();
    
    unsafe {
        std::ptr::copy_nonoverlapping(exported.as_ptr(), out_ptr, 80);
    }
    0
}
