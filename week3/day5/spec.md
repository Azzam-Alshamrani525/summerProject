# Spec: Book Tracker CLI

## 1. Objective

Build a Python command-line application, `booktracker.py`, that lets a user track books they are reading. Books are stored locally in a `books.json` file. No database, no GUI, no networking.

## 2. Inputs

All input comes from the user via terminal prompts (either an `input()`-driven menu loop or `argparse` commands). Required input fields when adding a book:

| Field  | Type   | Required | Constraint                                      |
|--------|--------|----------|--------------------------------------------------|
| title  | string | yes      | non-empty after trimming whitespace — reject and re-prompt on empty |
| author | string | yes      | non-empty after trimming whitespace — reject and re-prompt on empty |
| pages  | number | yes      | must be numeric (int)                             |
| genre  | string | yes      | free text                                         |
| status | string | yes      | must be exactly one of: `want to read`, `reading`, `finished` |

**Book identity:** titles are NOT unique (two books can share a title from different authors). Every book gets a system-assigned unique `id` (integer, auto-incremented starting at 1) when added. All lookups for "mark finished," "rate," etc. must select a book by `id`, not by title text. When listing books for the user to choose from, always display the `id` alongside the title so the user can pick correctly.

Additional input for existing books:
- **Mark finished:** user selects a book by `id`, its `status` is set to `finished`. If the book is already `finished`, do nothing and print a message stating it is already finished (not an error).
- **Rate a book:** user selects a book by `id`; integer 1–5, only accepted if `status` is `finished`
- **Filter:** by `status` (one of the three allowed values)
- **Search:** by `author` (partial match, case-insensitive)

## 3. Outputs

- Confirmation messages after add / update actions
- A listed view of books (all, or filtered by status/author) printed to the terminal, each line showing at minimum: `id`, title, author, status, rating
- If a list, filter, or search action returns zero results, print a message specific to that action (e.g. "No books match that status." / "No books found for that author.") — never reuse the generic "no books yet" message for a filtered/empty result, since that implies the whole library is empty
- Persisted state in `books.json` after every change
- Clear, human-readable error messages on invalid input (see Section 5)

## 4. Core Functional Requirements

1. Add a book (title, author, pages, genre, status)
2. Mark a book as finished
3. Rate a book 1–5 stars (finished books only; otherwise rating stays `null`)
4. List all books
5. Filter books by status
6. Search books by author

## 5. Validation Rules (must reject invalid input, not crash)

- `pages`: reject non-numeric input with an error message; re-prompt or return to menu
- `status`: reject any value not in `want to read` / `reading` / `finished`
- `rating`: reject values outside 1–5; reject rating attempts on books not marked `finished`
- Do not allow malformed data to be written to `books.json`

## 5a. Menu / Interaction Shape

Use a numbered `input()`-driven menu loop (not `argparse`) that repeats until the user exits:

```
1. Add a book
2. Mark a book finished
3. Rate a book
4. List all books
5. Filter by status
6. Search by author
7. Exit
```

- Invalid menu selections print an error and redisplay the menu — never crash
- Option 7 is the only way to exit; it terminates the loop cleanly

## 6. Data Storage Format

`books.json` — a JSON array of book objects:

```json
[
  {
    "id": 1,
    "title": "Dune",
    "author": "Frank Herbert",
    "pages": 412,
    "genre": "scifi",
    "status": "finished",
    "rating": 5
  }
]
```

- `id` is a system-assigned auto-incrementing integer, unique per book, assigned on add and never reused or changed
- `rating` is `null` unless `status` is `finished`
- File is created automatically if it doesn't exist; read/written on every change

## 7. Nice-to-Have (optional — implement only after core requirements pass)

- Sort books by rating
- Export book list to a plain text file
- Count total pages read across all finished books

## 8. Technical Constraints

- Language: Python (standard library only — `json`, optionally `argparse`)
- No external packages, no database
- Must run via: `python booktracker.py`
- Windows / Git Bash environment

## 9. Definition of Done

- All 6 core functional requirements (Section 4) work correctly
- Invalid input is rejected gracefully, never crashes the program
- Data persists correctly across runs via `books.json`
- Application runs successfully with `python booktracker.py`
- Application is containerized with a Dockerfile (per Docker convention) and runs via `docker run -it`

## 10. Out of Scope

- No authentication or multi-user support
- No GUI
- No remote/cloud storage
