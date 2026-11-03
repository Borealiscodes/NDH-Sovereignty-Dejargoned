pub mod manifold;
pub mod typeck;
pub mod codegen;
pub mod symplectic;
pub mod origami_engine; // <-- CRITICAL: MUST REGISTER MODULE HERE

use manifold::ManifoldEngine80D;
use typeck::DataPacketValidator;
use symplectic::SymplecticEngine;
use origami_engine::OrigamiFoldingEngine; // <-- CRITICAL: IMPORT STRUCT HERE

// ... Keep all existing Manifold and Symplectic bindings exactly as they are ...

// =========================================================================
// Origami Engine & Multimodal Control FFI Bindings
// =========================================================================

/// Allocates an OrigamiFoldingEngine instance on the heap and returns a raw pointer
#[no_mangle]
pub extern "C" fn create_origami_engine() -> *mut OrigamiFoldingEngine {
    Box::into_raw(Box::new(OrigamiFoldingEngine::new()))
}

/// Frees an OrigamiFoldingEngine instance safely from memory
#[no_mangle]
pub extern "C" fn free_origami_engine(ptr: *mut OrigamiFoldingEngine) {
    if !ptr.is_null() {
        unsafe {
            let _ = Box::from_raw(ptr);
        }
    }
}

/// Unified FFI gate processing multimodal array constraints down into stable folds
#[no_mangle]
pub extern "C" fn execute_origami_fold(
    engine_ptr: *mut OrigamiFoldingEngine,
    raw_state_ptr: *const f64,
    len: usize,
    folded_out_ptr: *mut f64,
) -> i32 {
    if engine_ptr.is_null() || raw_state_ptr.is_null() || folded_out_ptr.is_null() || len != 80 {
        return -1;
    }

    let raw_slice = unsafe { std::slice::from_raw_parts(raw_state_ptr, len) };
    
    match DataPacketValidator::validate_array_bounds(raw_slice) {
        Ok(sanitized_array) => {
            let engine = unsafe { &*engine_ptr };
            let folded_state = engine.synthesize_quantum_crease(&sanitized_array);
            
            // Intercept through the Lineage-Axis Moral Clarity Filter (LAMCF)
            if !engine.evaluate_moral_clarity_filter(&folded_state) {
                return -3; // Ethical boundary violation trigger code
            }

            unsafe {
                std::ptr::copy_nonoverlapping(folded_state.as_ptr(), folded_out_ptr, 80);
            }
            0
        }
        Err(_) => -2,
    }
}
