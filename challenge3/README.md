# Challenge 3: Boundary Safety (Input Validation & Crash Prevention)

## 1. The Engineering Concept
- Fail-Fast network boundaries using structured data modeling.
- Automatic type coercion and explicit runtime exceptions over silent payload failures.

## 2. The Chaos Simulation
The application expects standard input strings for grocery names and clean integers for quantities. However, the intern parses raw JSON request dictionaries directly without any predefined schemas.

### How to Run the Chaos Test:
1. Make sure your application stack is running.
2. Run the provided script in this folder:
   ```bash
   python simulate_chaos.py
   ```
3. **What happens:** The script fires a malformed JSON payload missing the exact dictionary keys the backend python process expects to read. The backend encounters an unhandled `KeyError`, causing the current request loop to completely fault out, returning an ugly 500 server crash back to the user interface.

## 3. Your Task
Stop guessing what incoming data looks like. You must define strict contracts.

1. Guide Claude to refactor all API paths to use explicit Pydantic models for incoming data payloads (`ItemCreate`, `ItemUpdate`).

2. Enforce strict field-level validation (e.g., shopping item names cannot be empty strings, and quantities must be strict positive integers greater than zero).

3. Confirm that when invalid or malformed data hit your server, the network boundary automatically drops the request with an HTTP `422 Unprocessable Entity` error code before it ever touches your database logic.
