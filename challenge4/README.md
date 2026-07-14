# Challenge 4: Data Integrity (Concurrent Overwrites)

## 1. The Engineering Concept
- The Lost Update Problem in distributed network applications.
- Concurrency control patterns (Optimistic Locking via object version tracking).

## 2. The Chaos Simulation
Imagine you and your partner are at different physical grocery stores updating the same kitchen shopping list simultaneously. There is 1 carton of Milk left on the list.
- You grab 2 more cartons and update the total quantity to 3.
- At the exact same millisecond, your partner grabs 1 more carton and updates the quantity to 2.

The intern's code reads the database state into Python memory, alters the integer variable, and blindly pushes a save statement back.

### How to Run the Chaos Test:
1. Ensure your application stack is up and active.
2. Run the concurrent automation script:
   ```bash
   python simulate_chaos.py
   ```
3. **What happens:** The script fires 10 rapid concurrent network requests mutating the exact same database row item at the identical millisecond. Because there is no concurrency control, updates read stale data and step over each other. The ultimate database tally becomes corrupt, and updates are permanently lost.

## 3. Your Task
You must guarantee state predictability when multi-tenant transactions strike data concurrently.

1. Instruct Claude to modify the shopping items database schema to include an integer `version` field.

2. Refactor the backend data mutation query to execute Optimistic Concurrency Control (OCC): ensure updates only commit if the `version` column in the database matches the version read at the start of the user's operation. On a successful save, increment the version value by 1.

3. If the row version has changed in the background, abort the current operation, reject the blind overwrite, and return an explicit HTTP `409 Conflict` error.

4. Update your system layer to safely intercept `409` errors and choose either an automatic retry loop or a clean UI banner warning the user that an update happened in parallel.
