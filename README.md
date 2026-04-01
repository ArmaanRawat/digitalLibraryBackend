# Digital Library Backend

A small but complete **REST API** for a digital library: user sign-up, catalog management with authors and categories, check-outs and returns, per-user borrowing history, overdue tracking, and automatic late fines. Built with **FastAPI** and **SQLite** for easy local development and deployment.

---

## What it does

- **Catalog** — Add books (with author and category as names; the API creates or reuses normalized author/category rows). List all titles, search by title/author/category, and list overdue loans still marked as borrowed past their due date.
- **Members** — Register and log in with email and password (stored in plaintext in this project; see [Security notes](#security-notes)).
- **Circulation** — Borrow a copy (decrements availability), return it (restores a copy), and fetch a user’s full borrow history.
- **Fines** — On return, overdue days are computed from the due date vs return date. Each day late costs a fixed amount; unpaid fine rows are stored per borrow record and exposed for a user.

---

## Tech stack

| Layer        | Choice                                                                  |
| ------------ | ----------------------------------------------------------------------- |
| Framework    | [FastAPI](https://fastapi.tiangolo.com/)                                |
| Database     | [SQLite](https://www.sqlite.org/) (`library.db`, created automatically) |
| Access layer | `sqlite3` (standard library), `Row` factory for dict-like rows          |
| Validation   | [Pydantic v2](https://docs.pydantic.dev/)                               |
| Server       | [Uvicorn](https://www.uvicorn.org/)                                     |
| Tests        | [pytest](https://pytest.org/) + `TestClient`                            |

> Dependencies also list **SQLAlchemy** and **python-jose**; the current app uses raw SQL and simple auth without JWT. You can wire these in for migrations or token-based auth later.

---

## Project layout

```
digital_library_backend/
├── app/
│   ├── main.py           # FastAPI app, routers, startup table creation
│   ├── database.py       # SQLite connection helper
│   ├── models.py         # `CREATE TABLE IF NOT EXISTS` schema
│   ├── schemas.py        # Pydantic request/response models
│   ├── crud.py           # Business logic: users, books, borrow, fines
│   └── routes/
│       ├── auth.py       # Register, login
│       ├── books.py      # CRUD-style catalog + search + overdue
│       ├── borrow.py     # Borrow, return, history
│       └── fines.py      # Fines by user
├── tests/
│   ├── test_books.py
│   └── test_borrow.py
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## Business rules (from code)

These constants live in `app/crud.py`:

- **Loan length:** 14 days from borrow date to due date.
- **Fine rate:** 5.0 (currency units) per calendar day late, charged only after the due date. On-time returns yield **0** fine.

Copies are tracked with `total_copies` and `available_copies`. A user cannot have two active borrows of the same book at once.

---

## Quick start (local)

**Requirements:** Python 3.11+ recommended (Dockerfile uses 3.11).

```bash
cd digital_library_backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API serves at `http://127.0.0.1:8000`. SQLite creates **`library.db`** in the working directory on first run (tables are ensured in `create_tables()`).

### Useful URLs

| URL          | Description                                  |
| ------------ | -------------------------------------------- |
| `GET /`      | Health-style welcome JSON                    |
| `GET /docs`  | Swagger UI (try all endpoints interactively) |
| `GET /redoc` | ReDoc                                        |

---

## Docker (preview)

```bash
docker build -t digital-library-api .
docker run -p 8000:8000 digital-library-api
```

Then open `http://localhost:8000/docs`.

---

## API reference (summary)

All routes are mounted at the **root** (no `/api` prefix).

### Auth

| Method | Path        | Body (JSON)                 | Notes                        |
| ------ | ----------- | --------------------------- | ---------------------------- |
| `POST` | `/register` | `name`, `email`, `password` | 400 if email exists          |
| `POST` | `/login`    | `email`, `password`         | 404 / 401 on bad credentials |

### Books

| Method | Path                      | Notes                                                  |
| ------ | ------------------------- | ------------------------------------------------------ |
| `POST` | `/books`                  | Body: `title`, `author`, `category`, `total_copies`    |
| `GET`  | `/books`                  | List with author/category names and `available_copies` |
| `GET`  | `/books/search?query=...` | `query` min length 1; 404 if no matches                |
| `GET`  | `/books/overdue`          | Active borrows with `due_date` before today            |

### Borrow & return

| Method | Path                        | Body                   | Notes                                                 |
| ------ | --------------------------- | ---------------------- | ----------------------------------------------------- |
| `POST` | `/borrow/{book_id}`         | `{ "user_id": <int> }` | Validates user, book, copies, duplicate active borrow |
| `POST` | `/return/{book_id}`         | `{ "user_id": <int> }` | Sets return + fine row; restores one copy             |
| `GET`  | `/borrow/history/{user_id}` | —                      | Ordered newest-first                                  |

### Fines

| Method | Path               | Notes                                      |
| ------ | ------------------ | ------------------------------------------ |
| `GET`  | `/fines/{user_id}` | Fines with book title, amount, `paid` flag |

Typical success responses wrap entities in `message` + `book` / `borrow_record` / `return_record` / `history` / `fines` keys as implemented in the route modules.

---

## Data model (SQLite)

- **users** — id, name, unique email, password, role (default `user`)
- **authors** / **categories** — id, unique name
- **books** — title, FKs to author/category, copy counts
- **borrow_records** — user, book, borrow/due/return dates, status (`borrowed` | `returned`)
- **fines** — one row per borrow_record (unique `borrow_record_id`), amount, `paid` (integer 0/1)

---

## Tests

```bash
pytest tests/ -v
```

Tests use `TestClient` against `app.main:app`. Because they hit a shared `library.db`, ordering can matter; for CI, point `DATABASE_NAME` at a temp file or run with an isolated DB if you extend the project.

---

## Security notes

This repository is suitable for learning and demos. **Passwords are not hashed** and there are **no JWT/session tokens**—`login` only validates and returns user fields. Before any production use, add password hashing (e.g. bcrypt), signed tokens or sessions, HTTPS, and input hardening. Consider moving secrets and DB path to environment variables.

---

## License

Add a license if you open-source this repo; none is specified in-tree.

---

Built as a **Digital Library Backend** micro-project: straightforward schema, clear separation between routes and `crud`, and FastAPI’s automatic OpenAPI docs for quick experimentation.
