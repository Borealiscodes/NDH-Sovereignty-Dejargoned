import ctypes
import os
import sys
import numpy as np

class CoreFFIBridge:
    def __init__(self, lib_path: str = None):
        if lib_path is None:
            ext = ".so" if not sys.platform.startswith("win32") else ".dll"
            # Fallback path checking standard compiled location
            lib_path = os.path.join(
                os.path.dirname(__file__), 
                f"../../../ndh_core_rust/target/release/libndh_core_rust{ext}"
            )
            
        if not os.path.exists(lib_path):
            raise FileNotFoundError(
                f"Compiled Rust shared library not found at: {lib_path}. Run 'make' first."
            )
            
        self.lib = ctypes.CDLL(lib_path)
        self._setup_bindings()

    def _setup_bindings(self):
        # --- Manifold Core Engine Bindings ---
        self.lib.create_manifold_engine.argtypes = []
        self.lib.create_manifold_engine.restype = ctypes.c_void_p

        self.lib.free_manifold_engine.argtypes = [ctypes.c_void_p]
        self.lib.free_manifold_engine.restype = None

        self.lib.execute_metric_evolution.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_double)
        ]
        self.lib.execute_metric_evolution.restype = ctypes.c_int32

        # Added bindings for the 80D Apex Gradient mapping wrapper
        self.lib.execute_compute_apex_gradient.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_double)
        ]
        self.lib.execute_compute_apex_gradient.restype = ctypes.c_int32

        # Added bindings for the 9D Radial Laplacian mapping wrapper
        self.lib.execute_compute_9d_radial_laplacian.argtypes = [
            ctypes.c_void_p,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.POINTER(ctypes.c_double)
        ]
        self.lib.execute_compute_9d_radial_laplacian.restype = ctypes.c_int32

        # --- Symplectic Engine Bindings ---
        self.lib.create_symplectic_engine.argtypes = []
        self.lib.create_symplectic_engine.restype = ctypes.c_void_p

        self.lib.free_symplectic_engine.argtypes = [ctypes.c_void_p]
        self.lib.free_symplectic_engine.restype = None

        self.lib.load_symplectic_state.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_size_t
        ]
        self.lib.load_symplectic_state.restype = ctypes.c_int32

        self.lib.export_symplectic_state.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_size_t
        ]
        self.lib.export_symplectic_state.restype = ctypes.c_int32


class NativeManifoldRuntime:
    def __init__(self, bridge: CoreFFIBridge):
        self.bridge = bridge
        self.engine_ptr = bridge.lib.create_manifold_engine()
        if not self.engine_ptr:
            raise MemoryError("Failed to initialize native Rust manifold engine allocation.")

    def update_metric(self, perturbation: np.ndarray) -> float:
        if perturbation.ndim != 1 or perturbation.shape != (80,):
            raise ValueError("Perturbation vector must be a flat 1D array of exactly 80 elements.")
            
        arr_data = np.ascontiguousarray(perturbation, dtype=np.float64)
        data_ptr = arr_data.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        
        out_scalar = ctypes.c_double(0.0)
        scalar_ptr = ctypes.byref(out_scalar)
        
        status = self.bridge.lib.execute_metric_evolution(
            self.engine_ptr, data_ptr, len(arr_data), scalar_ptr
        )
        
        if status == -1:
            raise RuntimeError("Native execution failed: Null pointer variant encountered.")
        elif status == -2:
            raise ValueError("Native execution failed: Invariant array validation bounds error.")
            
        return out_scalar.value

    def compute_apex_gradient(self, gradient_vector: np.ndarray) -> np.ndarray:
        """Executes Lean-verified coordinate normalization across the 80D manifold."""
        if gradient_vector.ndim != 1 or gradient_vector.shape != (80,):
            raise ValueError("Gradient vector must be a flat 1D array of exactly 80 elements.")
            
        arr_in = np.ascontiguousarray(gradient_vector, dtype=np.float64)
        in_ptr = arr_in.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        
        out_buffer = np.zeros(80, dtype=np.float64)
        out_ptr = out_buffer.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        
        status = self.bridge.lib.execute_compute_apex_gradient(
            self.engine_ptr, in_ptr, len(arr_in), out_ptr
        )
        
        if status == -1:
            raise RuntimeError("Native execution failed: Null pointer or dimensional constraint violation.")
        elif status == -2:
            raise ValueError("Native execution failed: Invariant array validation bounds error.")
            
        return out_buffer

    def compute_9d_radial_laplacian(self, r: float, f_prime: float, f_double_prime: float) -> float:
        """Executes Lean-verified hyperspherical diffusion using a safe epsilon boundary."""
        out_laplacian = ctypes.c_double(0.0)
        laplacian_ptr = ctypes.byref(out_laplacian)
        
        status = self.bridge.lib.execute_compute_9d_radial_laplacian(
            self.engine_ptr, r, f_prime, f_double_prime, laplacian_ptr
        )
        
        if status == -1:
            raise RuntimeError("Native execution failed: Null pointer encountered.")
            
        return out_laplacian.value

    def __del__(self):
        if hasattr(self, 'engine_ptr') and self.engine_ptr and hasattr(self, 'bridge'):
            self.bridge.lib.free_manifold_engine(self.engine_ptr)


class NativeSymplecticRuntime:
    def __init__(self, bridge: CoreFFIBridge):
        self.bridge = bridge
        self.engine_ptr = bridge.lib.create_symplectic_engine()
        if not self.engine_ptr:
            raise MemoryError("Failed to initialize native Rust symplectic engine allocation.")

    def load_state(self, state_vector: np.ndarray):
        if state_vector.ndim != 1 or state_vector.shape != (80,):
            raise ValueError("State vector must be a flat 1D array of exactly 80 elements.")
            
        arr_data = np.ascontiguousarray(state_vector, dtype=np.float64)
        data_ptr = arr_data.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        
        status = self.bridge.lib.load_symplectic_state(self.engine_ptr, data_ptr, len(arr_data))
        if status == -1:
            raise RuntimeError("Native symplectic load failed: Null pointer encountered.")
        elif status == -2:
            raise ValueError("Native symplectic load failed: Validation bounds error.")

    def export_state(self) -> np.ndarray:
        output_buffer = np.zeros(80, dtype=np.float64)
        buffer_ptr = output_buffer.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        
        status = self.bridge.lib.export_symplectic_state(self.engine_ptr, buffer_ptr, 80)
        if status == -1:
            raise RuntimeError("Native symplectic export failed: Error processing pointer tracking.")
            
        return output_buffer

    def __del__(self):
        if hasattr(self, 'engine_ptr') and self.engine_ptr and hasattr(self, 'bridge'):
            self.bridge.lib.free_symplectic_engine(self.engine_ptr)
