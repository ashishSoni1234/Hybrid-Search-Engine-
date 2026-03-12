# Break/Fix Log

- Minor compatibility issues between legacy rank-bm25 and latest NumPy versions: Ignored here as rank-bm25 0.2.2 usually bridges well or simply converts standard types.
- FAISS Windows vs Linux availability constraint: Relying heavily on CPU `faiss-cpu`, standard setups via `pip install faiss-cpu` handle wheel building on Python 3.11 for Windows mostly but might necessitate Visual Studio C++ build tools on Windows without prebuilt wheels.
- Evaluator normalizations: Using standard reciprocal ranks without bounding constraints.
