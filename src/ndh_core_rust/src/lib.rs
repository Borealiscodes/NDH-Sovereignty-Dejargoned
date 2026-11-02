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
