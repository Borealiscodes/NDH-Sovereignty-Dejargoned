pub mod manifold;
pub mod typeck;
pub mod codegen;

use manifold::ManifoldEngine80D;
use typeck::DataPacketValidator;

/// Opaque wrapper to manage the Rust engine across runtime environments
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
