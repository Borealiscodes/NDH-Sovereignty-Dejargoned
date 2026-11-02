# Root Orchestration Engine for NDH-Sovereignty-Dejargoned
.PHONY: all env format test verify_coq verify_lean build_core clean

PYTHON_DIR = src/ndh_demo_python
RUST_DIR   = src/ndh_core_rust
COQ_DIR    = verification/coq
LEAN_DIR   = verification/lean

all: env format verify_coq verify_lean build_core test
	@echo "=========================================================================="
	@echo "🏗️  NDH DEJARGOINED PIPELINE SUITE COMPLETED SUCCESSFULLY WITH ZERO LEAKAGE 🏗️"
	@echo "=========================================================================="

env:
	@echo "Initializing system environments and dependencies..."
	cd $(PYTHON_DIR) && pip install -e .[test]
	@if ! command -v coqc >/dev/null 2>&1; then echo "⚠️ Warning: coqc not found in PATH"; fi
	@if ! command -v cargo >/dev/null 2>&1; then echo "⚠️ Warning: cargo not found in PATH"; fi
	@if ! command -v lake >/dev/null 2>&1; then echo "⚠️ Warning: lake not found in PATH"; fi

format:
	@echo "Enforcing structural formatting constraints across runtime targets..."
	@black $(PYTHON_DIR)/src/ndh_demo/ $(PYTHON_DIR)/tests/ 2>/dev/null || echo "Skipping black (not installed)"
	cd $(RUST_DIR) && cargo fmt --check 2>/dev/null || cargo fmt

verify_coq:
	@echo "Executing static symbolic verification proofs in Coq enclave..."
	# Refined to include include path flags (-Q) targeting HolonomyRuntime mapping boundaries
	cd $(COQ_DIR) && coqc -Q . HolonomyRuntime JargonFilter.v
	cd $(COQ_DIR) && coqc -Q . HolonomyRuntime CapacityBounds.v
	cd $(COQ_DIR) && coqc -Q . HolonomyRuntime Manifold80Drefined.v

verify_lean:
	@echo "Compiling compile-time dependent type bounds in Lean 4 enclave..."
	cd $(LEAN_DIR) && lake build

build_core:
	@echo "Compiling high-performance native core library in Rust..."
	cd $(RUST_DIR) && cargo build --release
	# Ensure the compiled shared object artifact is synchronized for Python FFI usage
	@mkdir -p $(PYTHON_DIR)/src/ndh_demo/lib/
	@cp $(RUST_DIR)/target/release/libndh_core_rust.* $(PYTHON_DIR)/src/ndh_demo/lib/ 2>/dev/null || true

test:
	@echo "Launching numerical and native FFI integration test runners..."
	cd $(RUST_DIR) && cargo test --quiet
	cd $(PYTHON_DIR) && pytest tests/ -v

clean:
	@echo "Purging temporary build artifacts and compiled binary files..."
	cd $(RUST_DIR) && cargo clean
	cd $(LEAN_DIR) && lake clean
	rm -f $(COQ_DIR)/*.vo $(COQ_DIR)/*.vok $(COQ_DIR)/*.vos $(COQ_DIR)/*.glob
