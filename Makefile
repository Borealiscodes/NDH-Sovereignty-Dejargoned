# =========================================================================
# Root Orchestration Engine for NDH-Sovereignty-Dejargoned
# Routes multi-kernel build pipelines securely into bash verification scripts
# =========================================================================

.PHONY: all env format verify_coq verify_lean build_core test clean

PYTHON_DIR = src/ndh_demo_python
RUST_DIR   = src/ndh_core_rust
COQ_DIR    = verification/coq
LEAN_DIR   = verification/lean

# The default entryway now fires the complete, color-coded bash automation script
all:
	@chmod +x verify_pipeline.sh
	@./verify_pipeline.sh

env:
	@echo "[MAKE] Initializing python environments and FFI load paths..."
	cd $(PYTHON_DIR) && pip install -e .[test]

format:
	@echo "[MAKE] Enforcing formatting layout constraints..."
	@black $(PYTHON_DIR)/src/ndh_demo/ $(PYTHON_DIR)/tests/ 2>/dev/null || echo "Skipping black (not installed)"
	cd $(RUST_DIR) && cargo fmt --check 2>/dev/null || cargo fmt

verify_coq:
	@echo "[MAKE] Compiling refined Coq structural theorems..."
	cd $(COQ_DIR) && coqc -Q . HolonomyRuntime JargonFilter.v
	cd $(COQ_DIR) && coqc -Q . HolonomyRuntime CapacityBounds.v
	cd $(COQ_DIR) && coqc -Q . HolonomyRuntime Manifold80Drefined.v

verify_lean:
	@echo "[MAKE] Compiling Lean 4 dependent step constraints..."
	cd $(LEAN_DIR) && lake build

build_core:
	@echo "[MAKE] Compiling high-performance native core library in Rust..."
	cd $(RUST_DIR) && cargo build --release
	@mkdir -p $(PYTHON_DIR)/src/ndh_demo/lib/
	@cp $(RUST_DIR)/target/release/libndh_core_rust.* $(PYTHON_DIR)/src/ndh_demo/lib/ 2>/dev/null || true

test:
	@echo "[MAKE] Launching numerical and cross-modal test suites..."
	cd $(RUST_DIR) && cargo test --quiet
	cd $(PYTHON_DIR) && pytest tests/ -v

clean:
	@echo "[MAKE] Purging temporary build artifacts and compiled binaries..."
	cd $(RUST_DIR) && cargo clean
	cd $(LEAN_DIR) && lake clean
	rm -f $(COQ_DIR)/*.vo $(COQ_DIR)/*.vok $(COQ_DIR)/*.vos $(COQ_DIR)/*.glob
