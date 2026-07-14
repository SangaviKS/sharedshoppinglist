# 🧺 Shared Kitchen Shopping List — Starter Kit

A simple shared shopping list app for your apartment kitchen.  
Your roommates can all add items, mark them as purchased, and remove them.

---

## Prerequisites

Make sure you have the following installed:

- **Python 3.10+** — [python.org](https://python.org)
- **Node.js 18+** — [nodejs.org](https://nodejs.org)
- **npm** (comes with Node)

---

## Getting Started

You'll need **two terminal windows** open at the same time — one for the backend and one for the frontend.

---

### Terminal 1 — Start the Backend

```bash
cd backend

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn

# Start the server
uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

> **Note:** The shopping list lives entirely in memory. Every time you restart the backend, all items are gone. That's a known limitation of this starter — you'll fix it later!

---

### Terminal 2 — Start the Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in XXX ms

  ➜  Local:   http://localhost:5173/
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## Using the App

1. Type an item name (e.g. *"Oat Milk"*) into the first box.
2. Optionally type your name in the second box so your roommates know who added it.
3. Click **Add**.
4. When someone buys an item, click **✓ Got it** to mark it complete.
5. Click **✕** to remove an item from the list.

---

## Project Structure

```
capstone_uno/
├── backend/
│   └── main.py          # FastAPI app — all API routes live here
├── frontend/
│   ├── src/
│   │   └── App.jsx      # React single-page app
│   ├── index.html
│   └── package.json
└── README.md
```

---

## Known Limitations (Things to Improve Later!)

This is a **starter kit** — it's intentionally simple. Here are some things you'll notice break quickly once more than one person uses it:

- **No real database** — data disappears on every server restart.
- **Slow "Got it" button** — it contacts a mock notification service and takes ~3 seconds to respond. The whole server is frozen during that time!
- **No live updates** — if your roommate adds an item, you won't see it unless you refresh the page.
- **Duplicate items** — if you click "Add" twice quickly, you'll add the item twice.
- **Items can get "stuck"** — if two people click "Got it" at the exact same moment, the state can get confused.

These are all real problems you'll solve as you work through the capstone project. Good luck! 🚀
