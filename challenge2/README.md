# Challenge 2: Secure Identity & Authentication

## 1. The Engineering Concept
- Stateless Authentication via JSON Web Tokens (JWT).
- Secure credential hashing, password salting, and request authorization headers.

## 2. The Chaos Simulation
Right now, the kitchen shopping list is entirely public. Anyone on the internet who hits your live AWS URL can see, add, or wipe out your family's grocery list because there is no identity validation boundary at the API routing tier.

### How to Run the Chaos Test:
1. Ensure your app is running.
2. Open an anonymous terminal or a browser incognito window.
3. Execute a blind DELETE or POST request via cURL:
   ```bash
   curl -X POST http://localhost:8000/items -H "Content-Type: application/json" -d '{"name": "Hacked"}'
   ```
4. **What happens:** The server blindly accepts the input from an anonymous, unauthenticated source.

## 3. Your Task
You must lock down the application and bind lists to specific authenticated kitchen profiles.

1. Have Claude implement a `users` table schema in PostgreSQL storing `username` and hashed passwords (using a secure library like `bcrypt` or `passlib`). Never store plain-text credentials.

2. Instruct Claude to build a login endpoint (`/auth/login`) that validates passwords and issues an encrypted, time-expiring JWT access token.

3. Refactor your React app to capture this token, store it in local state/cookies securely, and automatically inject it into an `Authorization: Bearer <TOKEN>` HTTP header for subsequent requests.

4. Update the FastAPI backend using dependency injection to reject any incoming requests missing a valid, signature-verified JWT.
