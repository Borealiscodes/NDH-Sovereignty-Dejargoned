use crate::manifold::MANIFOLD_DIM;

/// Formally validates input tensors to protect the core processing manifold
pub struct DataPacketValidator;

impl DataPacketValidator {
    /// Inspects an incoming slice to guarantee complete dimension matching and numerical safety
    pub fn validate_array_bounds(data: &[f64]) -> Result<[f64; MANIFOLD_DIM], &'static str> {
        if data.len() != MANIFOLD_DIM {
            return Err("Input array bounds violation: Data vector length must be exactly 80.");
        }

        let mut sanitized_array = [0.0; MANIFOLD_DIM];
        for i in 0..MANIFOLD_DIM {
            let val = data[i];
            // Filter out NaN and Infinite entries before they poison the matrix layers
            if val.is_nan() || val.is_infinite() {
                return Err("Input tensor contains corrupt elements: NaN or Infinite values detected.");
            }
            sanitized_array[i] = val;
        }

        Ok(sanitized_array)
    }
}
