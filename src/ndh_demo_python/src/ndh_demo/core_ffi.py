import ctypes
import os
import sys
import numpy as np

class CoreFFIBridge:
    def __init__(self, lib_path: str = None):
        if lib_path is None:
            # Locate the compiled target binary depending on standard OS extensions
            ext = ".so" if not sys.platform.startswith("win32") else ".dll"
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
        # void* create_manifold_engine()
        self.lib.create_manifold_engine.argtypes = []
        self.lib.create_manifold_engine.restype = ctypes.c_void_p

        # void free_manifold_engine(void* ptr)
        self.lib.free_manifold_engine.argtypes = [ctypes.c_void_p]
        self.lib.free_manifold_engine.restype = None

        # int32 execute_metric_evolution(void* engine, double* perturbation, size_t len, double* out_scalar)
        self.lib.execute_metric_evolution.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_double)
        ]
        self.lib.execute_metric_evolution.restype = ctypes.c_int32

class NativeManifoldRuntime:
    def __init__(self, bridge: CoreFFIBridge):
        self.bridge = bridge
        self.engine_ptr = bridge.lib.create_manifold_engine()
        if not self.engine_ptr:
            raise MemoryError("Failed to initialize native Rust manifold engine allocation.")

    def update_metric(self, perturbation: np.ndarray) -> float:
        if perturbation.ndim != 1 or perturbation.shape[0] != 80:
            raise ValueError("Perturbation vector must be a flat 1D array of exactly 80 elements.")
            
        # Ensure array data is contiguous and uses standard float64 encoding
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

    def __del__(self):
        if hasattr(self, 'engine_ptr') and self.engine_ptr and hasattr(self, 'bridge'):
            self.bridge.lib.free_manifold_engine(self.engine_ptr)
