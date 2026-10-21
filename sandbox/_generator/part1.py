"""Notebook content for lectures 00-10."""
from builder import SETUP_SQL, code, md, try_sql_demo

def _intro(no, title, module, src, goals, extra=""):
    g = "\n".join(f"- {x}" for x in goals)
    head = f"# {no}. {title}\n\n*Module: {module} · Companion summary: `lectures/{src}` · SQL engine: SQLite (in-memory)*\n"
    block = f"""
## What you will study

{g}
{extra}
---
## Setup — build the sample database this notebook runs on
*Run the cell below first: it creates an in-memory SQLite database and the `q()` helper that prints every query's result set.*"""
    return md(head + block)

def nb00():
    return [
        md("# 00. START HERE — your SQL study sandbox\n\n"
           "*Companion to: `lectures/01…29-*.md` and `index.html` (the cheatsheet)*"),
        md("""## How to use this sandbox

One notebook per course lecture, named and ordered like the course:

| Notebooks | Course module | Topic |
|---|---|---|
| `02…04` | 1 — Basics | definitions, DDL vs DML, relational/ER model |
| `05…06` | 2 — Data definition | CREATE TABLE, ALTER/DROP/TRUNCATE |
| `07…10` | 3 — DML | INSERT, SELECT/WHERE, COUNT/DISTINCT/LIMIT, UPDATE/DELETE |
| `11…15` | 4 — Advanced querying | LIKE/BETWEEN/IN, ORDER BY, GROUP BY/HAVING, functions, dates |
| `16…20` | 5 — Multi-table | sub-queries, multiple tables, JOINs |
| `21…26` | 6 — Python access | DB-API, SQL Magic, CSVs, metadata, EDA |
| `27…29` | 7 — Advanced server | Views, Stored Procedures, ACID |

Each notebook is **self-contained**: its first setup cell builds the in-memory sample
database it needs, so you can open them in any order (and re-run them as often as you
like — nothing persists). Every concept pair is *explanation → runnable example*, and
each notebook ends with **"Your turn" exercises** (solutions included)."""),
        md("""## Launching

```bash
jupyter lab .       # or:  jupyter notebook .
```

You only need Jupyter + Python's built-in `sqlite3`. Notebooks `24` and `26` also use
`pandas` / `seaborn` (install if needed):

```bash
pip install pandas seaborn matplotlib ipykernel jupyter
```

## A note on dialect

The course teaches DB2-flavored SQL. SQLite (your runnable engine) is very close but
differs in a few places; wherever they differ you'll see a **📕 dialect note** showing
both spellings — a great habit for reading real-world SQL."""),
        code("""# Sanity check — run me!
import sqlite3, sys
print('Python:', sys.version.split()[0])
print('SQLite engine in this Python:', sqlite3.sqlite_version)
print('SELECT 1+1 ->', sqlite3.connect(':memory:').execute('SELECT 1+1').fetchone()[0])"""),
    ]

def nb01():
    return [
        _intro("01", "Course Welcome & Overview", "Intro", "01-course-welcome-and-overview.md",
               ["the six-module roadmap and where each SQL topic lives",
                "what SQL does in the data-science workflow and what Python adds to it"]),
        md("""## The roadmap (from the video)

| Module | Topic |
|---|---|
| 1 | SQL basics — DML: INSERT / SELECT / UPDATE / DELETE |
| 2 | DDL — CREATE / ALTER / DROP / TRUNCATE tables |
| 3 | Built-in functions, sub-queries, multiple tables, joins |
| 4 | Python for databases — Jupyter, DB-API, SQL Magic, EDA |
| 5 | Hands-on project on real-world data |
| 6 | Advanced — Views, Stored Procedures, ACID, Inner & Outer JOINs |

**Your goal while moving through this sandbox:** after each module, come back here and
tick the module off *only if you can do it from memory*."""),
        code("""# A checklist you can re-visit
roadmap = [
    "Module 1: I can create/populate a table, select rows with WHERE",
    "Module 2: I can create and change table structure (DDL)",
    "Module 3: I can use functions, sub-queries and multiple tables",
    "Module 4: I can connect to a database from Python and load/query data",
    "Module 5: I completed the course's real-data project",
    "Module 6: I can write joins, views, procedures and transactions",
]
for i, item in enumerate(roadmap, 1):
    print(f'  [ ] {item}')"""),
        md("""## A taste of what's coming

One tiny SQL statement — you'll understand *every word* after lecture 08:"""),
        code(SETUP_SQL + """

q("SELECT 'Hello from SQL' AS message, 1+1 AS two")"""),
    ]

def nb02():
    return [
        _intro("02", "Data, Databases & RDBMS", "1 — Basics", "02-sql-databases-and-rdbms.md",
               ["define data, database, DBMS/RDBMS and SQL",
                "run the five basic SQL commands (CREATE, INSERT, SELECT, UPDATE, DELETE)"]),
        code(SETUP_SQL),
        md("## 📗 Key definitions\n\n"
           "- **Data** — a collection of facts (words, numbers, pictures). A business's most critical asset.\n"
           "- **Database** — a repository of data; supports adding, modifying, querying.\n"
           "- **DBMS/RDBMS** — the software tools controlling access, organization, storage (MySQL, Oracle, DB2, SQLite…).\n"
           "- **SQL** — Structured Query Language: how we ask the database for what we want."),
        md("""## 🧪 The five basic commands — all of them, live

**1️⃣ CREATE** — build a table with named columns and datatypes:
```sql
CREATE TABLE people (id INTEGER PRIMARY KEY, name TEXT, age INTEGER, city TEXT)
```
*Run the next cell, then each following one.*"""),
        code("q(\"CREATE TABLE people (id INTEGER PRIMARY KEY, name TEXT, age INTEGER, city TEXT)\")"),
        md("**2️⃣ INSERT** — populate the table (Create):"),
        code("""q("INSERT INTO people VALUES (1, 'Raul', 41, 'Toronto')")
q("INSERT INTO people VALUES (2, 'Rav', 35, 'Markham')")
q("INSERT INTO people VALUES (3, 'Emma', 29, 'Sydney')")
q("SELECT * FROM people")"""),
        md("**3️⃣ SELECT** — read (Read). Restrict with **WHERE** and choose **columns**:"),
        code("q(\"SELECT name, city FROM people WHERE age > 30\")"),
        md("**4️⃣ UPDATE** — change a row (Update). The WHERE clause picks *which* row:"),
        code("""q("UPDATE people SET city = 'Ottawa' WHERE id = 1")
q("SELECT * FROM people")"""),
        md("**5️⃣ DELETE** — remove a row (Delete):"),
        code("""q("DELETE FROM people WHERE id = 3")
q("SELECT * FROM people")"""),
        md("""## 💡 Tips & tricks

- These five commands are **identical on every RDBMS** (MySQL, Oracle, DB2, Postgres…).
  Dialects differ on advanced stuff, not on CRUD.
- `database ≈ DBMS ≈ database server` — the terms are used interchangeably in practice.

## 🎯 Your turn

1. INSERT a 4th person with your own name into `people`, then SELECT it.
2. UPDATE that person's `city` without touching anyone else's row."""),
        code("""# ✏️ Your work here
"""),
        code("""# 💡 Solution 1
q("INSERT INTO people VALUES (4, 'You', 30, 'Cairo')")
q("SELECT * FROM people WHERE id = 4")

# 💡 Solution 2 — WHERE on the unique id keeps the update surgical
q("UPDATE people SET city = 'Giza' WHERE id = 4")
q("SELECT * FROM people WHERE id = 4")"""),
    ]

def nb03():
    return [
        _intro("03", "DDL vs DML", "1 — Basics", "03-types-of-sql-statements-ddl-vs-dml.md",
               ["name the four DDL statements and what each does",
                "map the four DML statements to CRUD",
                "distinguish structure changes from data changes in practice"]),
        code(SETUP_SQL),
        md("""## 📗 The two families

**DDL — Data Definition Language** (touches *structure*): `CREATE`, `ALTER`,
`TRUNCATE`, `DROP`.
**DML — Data Manipulation Language** (touches *content*, the CRUD cycle):
`INSERT` (Create), `SELECT` (Read), `UPDATE` (Update), `DELETE` (Delete)."""),
        md("## 🧪 DDL in action — building the container"),
        code("q(\"\"\"\nCREATE TABLE notes (\n    id     INTEGER PRIMARY KEY,\n    body   TEXT,\n    author TEXT\n)\n\"\"\")"),
        md("## 🧪 DML in action — working with what's inside"),
        code("""q("INSERT INTO notes VALUES (1, 'hello', 'Raul')")
q("INSERT INTO notes VALUES (2, 'world', 'Rav')")
q("UPDATE notes SET author = 'Ana' WHERE id = 2")
q("SELECT * FROM notes")"""),
        md("## 🧪 DELETE (DML) vs DROP (DDL) on the same table"),
        code("""# DML: remove rows — table survives, schema survives
q("DELETE FROM notes WHERE id = 1")
q("SELECT * FROM notes")
q("SELECT * FROM sqlite_master WHERE name = 'notes' AND type = 'table'")"""),
        code("""# DDL: remove the whole container
q("DROP TABLE notes")
try:
    conn.execute("SELECT * FROM notes")
except sqlite3.OperationalError as e:
    print('Dropping the table also removed its schema:', repr(e))"""),
        md("""## 💡 Tips & tricks

- **DELETE is DML, TRUNCATE is DDL** — a favorite interview question.
- Both `TRUNCATE` and `DELETE` without a WHERE empty a table; TRUNCATE is the faster,
  storage-resetting one — but SQLite only has `DELETE FROM table` (no TRUNCATE).
  📕 Dialect note:
  ```sql
  TRUNCATE TABLE notes IMMEDIATE;   -- DB2 / MySQL: fast empty + storage reset
  DELETE FROM notes;                -- SQLite's spelling
  ```

## 🎯 Your turn

1. Recreate `notes` with an extra column `priority INTEGER`.
2. Empty it two different ways (DELETE; then DROP) and check `sqlite_master` in between."""),
        code("""# 💡 Solution
q("CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT, author TEXT, priority INTEGER)")
q("DELETE FROM notes")
q("SELECT count(*) FROM notes")
q("DROP TABLE notes")
try:
    q("SELECT * FROM notes")
except sqlite3.OperationalError as e:
    print('gone:', e)"""),
    ]

def nb04():
    return [
        _intro("04", "Relational Model & ER Model", "1 — Basics", "04-database-concepts-relational-model.md",
               ["map entities → tables, attributes → columns, values → rows",
                "choose CHAR vs VARCHAR-style types for the job",
                "see primary keys and foreign keys enforce relationships"]),
        code(SETUP_SQL),
        md("""## 📗 ER → relational mapping

| ER concept | Relational result | Library example |
|---|---|---|
| Entity (rectangle in a diagram) | **Table** | AUTHOR, BOOK |
| Attribute (oval) | **Column** | title, year, lastname |
| Data values | **Rows** | ('A1', 'Chong', ...) |
| Identifier | **Primary key** | book_id |
| Attribute referencing another table's PK | **Foreign key** | book.author_id |

Types: `INTEGER` / `DECIMAL` for numbers, `DATE`/timestamp types for dates, and for
strings: fixed-length codes get CHAR-style types, human-entered text gets VARCHAR-style.
(SQLite only formalizes INTEGER / REAL / TEXT / BLOB / NULL — sizes are advisory.)"""),
        md("## 🧪 Build the library mini-model — BOOK references AUTHOR"),
        code("""q(\"\"\"
CREATE TABLE author (
    author_id TEXT PRIMARY KEY,     -- equivalent of CHAR(2) but sized freely
    lastname  TEXT NOT NULL,
    firstname TEXT NOT NULL,
    email TEXT, city TEXT, country TEXT
)
\"\"\")
q(\"\"\"
CREATE TABLE book (
    book_id  TEXT PRIMARY KEY,
    title    TEXT,                  -- VARCHAR-style: varies per book
    pages    INTEGER,
    author_id TEXT REFERENCES author(author_id)
)
\"\"\")"""),
        md("## 🧪 PRIMARY KEY enforces uniqueness; FOREIGN KEY enforces the link"),
        code("""q("INSERT INTO author VALUES ('A1', 'Chong', 'Raul', null, 'Toronto', 'CA')")
try:
    # duplicate primary key — the db refuses
    q("INSERT INTO author VALUES ('A1', 'Faker', 'Fake', null, null, null)")
except sqlite3.IntegrityError as e:
    print('PRIMARY KEY refused a duplicate:', repr(e))
try:
    # a book pointing at an author that does not exist
    q("INSERT INTO book VALUES ('B1', 'A Book', 200, 'A9')")
except sqlite3.IntegrityError as e:
    print('FOREIGN KEY refused an unknown author:', repr(e))
q("INSERT INTO book VALUES ('B1', 'The Little Prince', 292, 'A1')")  # now valid
q("SELECT * FROM book")"""),
        md("## 🧪 Inspect the model you built (a taste of lecture 25)"),
        code("""q("SELECT name, type FROM sqlite_master WHERE type IN ('table')")"""),
        md("""## 💡 Tips & tricks

- Sketch the ERD first, SQL second — joins are transcribed from PK→FK links (lecture 18).
- `CHAR`-style for truly fixed lengths (country codes, ISBN), `VARCHAR`-style for titles,
  names, emails.

## 🎯 Your turn

1. Add entity `BORROWER (borrower_id, lastname, country)` yourself.
2. Add entity `LOAN (borrower_id, book_id, loan_date)` whose two keys reference the
   other tables — then try inserting a loan for an unknown borrower to see the FK fire."""),
        code("""# 💡 Solution
q("CREATE TABLE borrower (borrower_id TEXT PRIMARY KEY, lastname TEXT, country TEXT)")
q("CREATE TABLE loan (borrower_id TEXT REFERENCES borrower(borrower_id), book_id TEXT REFERENCES book(book_id), loan_date TEXT)")
q("INSERT INTO borrower VALUES ('B1', 'Ali', 'IN')")
try:
    q("INSERT INTO loan VALUES ('B99', 'B1', '2024-01-01')")
except sqlite3.IntegrityError as e:
    print('foreign key enforced:', repr(e))
q("INSERT INTO loan VALUES ('B1', 'B1', '2024-01-01')")
q("SELECT * FROM loan")"""),
    ]

def nb05():
    return [
        _intro("05", "CREATE TABLE", "2 — Data definition", "05-create-table.md",
               ["write CREATE TABLE with column name, datatype, constraints",
                "use PRIMARY KEY for uniqueness and NOT NULL for required fields",
                "avoid the classic trailing-comma syntax error"]),
        code(SETUP_SQL),
        md("""## 🧪 The lookup-table example from the course

`provinces` — tiny 2-letter codes (CHAR-style) vs full names (VARCHAR-style):
```sql
CREATE TABLE provinces (id CHAR(2) PRIMARY KEY NOT NULL, name VARCHAR(24))
```
"""),
        code("q(\"CREATE TABLE provinces (id TEXT PRIMARY KEY NOT NULL, name TEXT NOT NULL)\")"),
        md("## 🧪 The full AUTHOR table from the course, with constraints"),
        code("""q(\"\"\"
CREATE TABLE author (
    author_id TEXT PRIMARY KEY NOT NULL,
    lastname  TEXT NOT NULL,
    firstname TEXT NOT NULL,
    email     TEXT,
    city      TEXT,
    country   TEXT
)
\"\"\")
q(\"\"\"
INSERT INTO author (author_id, lastname, firstname, email, city, country)
VALUES ('A1', 'Chong', 'Raul', 'RFC@ca.ibm.com', 'Toronto', 'CA')
\"\"\")
q("SELECT * FROM author")"""),
        md("## 🧪 The constraints, firing live"),
        try_sql_demo(
    "conn.execute(\"CREATE TABLE author (author_id TEXT PRIMARY KEY, lastname TEXT)\")",
    "a table name can only be created once"),
        try_sql_demo(
    "conn.execute(\"INSERT INTO author VALUES ('A1', 'Faker', 'Fake', 'x@x.com', 'XCity', 'XX')\")",
    "PRIMARY KEY refuses duplicate author_id"),
        try_sql_demo(
    "conn.execute(\"INSERT INTO author VALUES ('A5', null, 'NoName')\")",
    "NOT NULL refuses a missing lastname"),
        md("""## 💡 Tips & tricks

- The **last column has no trailing comma** — the classic beginner CREATE error.
  ```sql
  -- ❌ trailing comma: id CHAR(2), name VARCHAR(24),
  -- ✅ id CHAR(2) PRIMARY KEY NOT NULL, name VARCHAR(24)
  ```
- Designate the primary key at creation time; retrofitting uniqueness into a populated
  table is painful.
- 📕 Dialect note — SQLite ignores VARCHAR(n) length limits (they're advisory); DB2, MySQL
  and Oracle enforce them.

## 🎯 Your turn

1. CREATE `student (student_id, name, email)` with the right two constraints so that
   ids are unique and names are mandatory.
2. Prove both constraints fire with your own INSERT attempts."""),
        code("""# 💡 Solution
q("CREATE TABLE student (student_id TEXT PRIMARY KEY NOT NULL, name TEXT NOT NULL, email TEXT)")
q("INSERT INTO student VALUES ('S1', 'Dup', 'x@y.z')")   # this one lands
try: conn.execute("INSERT INTO student VALUES ('S1', 'Dup2', 'x@y.z')")
except sqlite3.IntegrityError as e: print('dup id:', e)
try: conn.execute("INSERT INTO student VALUES ('S2', null, 'x@y.z')")
except sqlite3.IntegrityError as e: print('no name:', e)
q("UPDATE student SET name = 'You' WHERE student_id = 'S1'")
q("SELECT * FROM student")"""),
    ]

def nb06():
    return [
        _intro("06", "ALTER · DROP · TRUNCATE", "2 — Data definition", "06-alter-drop-and-truncate.md",
               ["add and remove columns with ALTER TABLE",
                "know why changing a populated column's datatype can fail",
                "choose between DELETE-rows, TRUNCATE and DROP TABLE"]),
        code(SETUP_SQL),
        md("## 🧪 Start from the author table (course story arc)"),
        code("""q("CREATE TABLE author (author_id TEXT PRIMARY KEY, lastname TEXT NOT NULL, firstname TEXT NOT NULL, email TEXT, city TEXT, country TEXT)")
q("INSERT INTO author VALUES ('A1', 'Chong', 'Raul', 'RFC@ca.ibm.com', 'Toronto', 'CA')")
q("SELECT * FROM author")"""),
        md("## 🧪 ALTER: add a telephone number column"),
        code("""q("ALTER TABLE author ADD COLUMN telephone_number TEXT")   # strings, not numbers!
q("UPDATE author SET telephone_number = '+1 (416) 555-0100' WHERE author_id = 'A1'")
q("SELECT * FROM author")"""),
        md("""**📕 Dialect note — changing a column's datatype.** The course shows
```sql
ALTER TABLE author MODIFY telephone_number CHAR(20);     -- DB2 / MySQL
ALTER TABLE author ALTER COLUMN telephone_number CHAR(20); -- SQL Server syntax
```
SQLite **cannot change a column's type at all** — the standard recipe is:
create the corrected table, `INSERT INTO new SELECT … FROM old`, drop old, rename new:"""),
        code("""q("CREATE TABLE author_v2 (author_id TEXT PRIMARY KEY, lastname TEXT NOT NULL, firstname TEXT NOT NULL, email TEXT, city TEXT, country TEXT, telephone_number TEXT)")
q("INSERT INTO author_v2 SELECT author_id, lastname, firstname, email, city, country, telephone_number FROM author")
q("DROP TABLE author")
q("ALTER TABLE author_v2 RENAME TO author")
q("SELECT * FROM author")"""),
        md("## 🧪 ALTER again: drop the column when the spec changes"),
        code("""q("ALTER TABLE author DROP COLUMN telephone_number")   # SQLite ≥ 3.35 supports this
q("SELECT * FROM author")"""),
        md("## 🧪 DROP TABLE vs TRUNCATE/DELETE"),
        code("""q("CREATE TABLE scratch (x INTEGER)")
q("INSERT INTO scratch VALUES (1),(2)")
q("DELETE FROM scratch")   # SQLite's TRUNCATE equivalent
q("SELECT count(*) AS rows_left FROM scratch")   # table survives, 0 rows
q("DROP TABLE scratch")   # DDL: container gone
"""),
        md("""## 💡 Tips & tricks

- Store phone numbers as **strings** — `( ) + -` break numeric columns.
- Mnemonic: TRUNCATE = fast *empty*; DROP = *demolish*. Neither takes a WHERE.

## 🎯 Your turn

1. `ALTER TABLE author ADD COLUMN nickname TEXT`, populate it, then drop the column again.
2. Build `tmp1`, empty it with DELETE, and prove the empty table still exists."""),
        code("""# 💡 Solution
q("ALTER TABLE author ADD COLUMN nickname TEXT")
q("UPDATE author SET nickname = 'RC' WHERE author_id = 'A1'")
q("SELECT author_id, nickname FROM author")
q("ALTER TABLE author DROP COLUMN nickname")
q("SELECT * FROM author")
q("CREATE TABLE tmp1 (x INTEGER)")
q("INSERT INTO tmp1 VALUES (9)")
q("DELETE FROM tmp1")
q("SELECT count(*) AS n FROM tmp1")"""),
    ]

def nb07():
    return [
        _intro("07", "INSERT Statement", "3 — DML", "07-insert-statement.md",
               ["write the INSERT statement: table, column list, VALUES",
                "insert one row at a time and several rows in one statement",
                "keep value-count = column-count, always"]),
        code(SETUP_SQL),
        md("## 🧪 One row at a time — with the full column list"),
        code("""q("CREATE TABLE author (author_id TEXT PRIMARY KEY, lastname TEXT NOT NULL, firstname TEXT NOT NULL, email TEXT, city TEXT, country TEXT)")
q(\"\"\"
INSERT INTO author (author_id, lastname, firstname, email, city, country)
VALUES ('A1', 'Chong', 'Raul', 'RFC@ca.ibm.com', 'Toronto', 'CA')
\"\"\")
q("SELECT * FROM author")"""),
        md("""## 🧪 Multiple rows in ONE statement (the course's second method)

Each row is its own `( ... )`; rows are separated by commas:"""),
        code("""q(\"\"\"
INSERT INTO author (author_id, lastname, firstname, email, city, country) VALUES
    ('A2', 'Ahuja', 'Rav',  'RA@ca.ibm.com', 'Markham',  'CA'),
    ('A3', 'Katta', 'Lakshmi', 'LK@in.ibm.com', 'Bengaluru', 'IN')
\"\"\")
q("SELECT * FROM author")"""),
        md("## 🧪 The golden rule, violated live"),
        try_sql_demo(
    "conn.execute(\"INSERT INTO author (author_id, lastname, firstname) VALUES ('A9', 'Solo')\")",
    "2 columns in the list but 3 values given → refused"),
        md("""## 💡 Tips & tricks

- **Always name your columns** — positional INSERTs break when the schema changes.
- Text values need quotes ('Chong'); numbers don't. 'A1' is a string because the column
  is TEXT/CHAR.
- 📕 Note: SQLite additionally supports `INSERT OR IGNORE` / `INSERT OR REPLACE` for
  constraint collisions — handy for study loops.

## 🎯 Your turn

1. Insert two more authors (your own data!) in one multi-row statement.
2. Insert a row into a NEW table `publisher` you invent with 3 columns."""),
        code("""# 💡 Solution
q(\"\"\"
INSERT INTO author (author_id, lastname, firstname, email, city, country) VALUES
    ('A4', 'Ali', 'Nadia', 'NA@eg.ibm.com', 'Cairo', 'EG'),
    ('A5', 'Roux', 'Claire', 'CR@fr.ibm.com', 'Lyon', 'FR')
\"\"\")
q("SELECT * FROM author")
q("CREATE TABLE publisher (pub_id TEXT PRIMARY KEY, name TEXT NOT NULL, founded INTEGER)")
q("INSERT INTO publisher (pub_id, name, founded) VALUES ('P1', 'OReilly-Demo', 1978)")
q("SELECT * FROM publisher")"""),
    ]

def nb08():
    return [
        _intro("08", "SELECT · WHERE · Predicates", "3 — DML", "08-select-statement-where-clause.md",
               ["retrieve all rows / a subset of columns / a restricted set of rows",
                "define predicate (true / false / unknown) and use it in WHERE",
                "use all six comparison operators"]),
        code(SETUP_SQL),
        md("## 🧪 Sample data — the BOOK table from the course"),
        code("""q("CREATE TABLE book (book_id TEXT PRIMARY KEY, title TEXT, pages INTEGER, year INTEGER)")
q(\"\"\"
INSERT INTO book VALUES
    ('B1', 'The Little Prince',   292, 1943),
    ('B2', 'Journey to the West', 298, 1592),
    ('B3', 'SQL Basics',          150, 2018),
    ('B4', 'Data Science Handbook', 400, 2020),
    ('B5', 'A Short Story',        45, 2022)
\"\"\")
q("SELECT * FROM book")"""),
        md("## 🧪 Choose your columns — output order follows the SELECT list"),
        code("q(\"SELECT book_id, title FROM book\")"),
        md("## 🧪 WHERE with a predicate — restrict to rows where it evaluates TRUE"),
        code("""q("SELECT book_id, title FROM book WHERE book_id = 'B1'")
q("SELECT title, pages FROM book WHERE pages > 200")"""),
        md("## 🧪 All six comparison operators, one query each"),
        code("""print('equal to            ='); q("SELECT title FROM book WHERE book_id = 'B2'")
print('greater than        >'); q("SELECT title FROM book WHERE pages > 290")
print('less than           <'); q("SELECT title FROM book WHERE pages < 150")
print('greater or equal   >='); q("SELECT title FROM book WHERE pages >= 292")
print('less or equal      <='); q("SELECT title FROM book WHERE pages <= 292")
print('not equal           <>'); q("SELECT title FROM book WHERE book_id <> 'B1'")"""),
        md("## 🧪 Combine predicates with AND / OR"),
        code("q(\"SELECT title FROM book WHERE pages > 200 AND year > 2018\")\nq(\"SELECT title FROM book WHERE year = 1943 OR pages = 45\")"),
        md("""## 💡 Tips & tricks

- Avoid `SELECT *` in production code: name the columns (less traffic, self-documenting,
  survives schema changes).
- 'B1' compares strings, 292 compares numbers — quotes matter.

## 🎯 Your turn

1. Titles of books with `pages >= 150` AND `year >= 2018`.
2. All columns of books that are NOT 'B3'."""),
        code("""# 💡 Solution
q("SELECT title FROM book WHERE pages >= 150 AND year >= 2018")
q("SELECT * FROM book WHERE book_id <> 'B3'")"""),
    ]

def nb09():
    return [
        _intro("09", "COUNT · DISTINCT · LIMIT", "3 — DML", "09-count-distinct-limit.md",
               ["count rows matching query criteria",
                "remove duplicate values from a result set",
                "peek at a result set with LIMIT instead of retrieving everything"]),
        code(SETUP_SQL),
        md("## 🧪 Sample data — the MEDALS table (countries can win the same medal repeatedly)"),
        code("""q("CREATE TABLE medals (country TEXT, medaltype TEXT, year INTEGER, athlete TEXT)")
q(\"\"\"
INSERT INTO medals VALUES
    ('CANADA','GOLD',2018,'Smith'),  ('CANADA','GOLD',2016,'Tremblay'),
    ('CANADA','SILVER',2018,'Lee'),  ('CHINA','GOLD',2018,'Wang'),
    ('CHINA','GOLD',2016,'Li'),      ('UK','GOLD',2018,'Brown'),
    ('UK','SILVER',2016,'Cox'),      ('USA','GOLD',2018,'Davis'),
    ('USA','SILVER',2018,'Miller'),  ('USA','BRONZE',2016,'Taylor'),
    ('UK','BRONZE',2018,'Wilson'),   ('CHINA','BRONZE',2018,'Zhang'),
    ('CANADA','BRONZE',2016,'Clark')
\"\"\")
q("SELECT * FROM medals")"""),
        md("## 🧪 COUNT — how many rows?"),
        code("""q("SELECT COUNT(*) FROM medals")
q("SELECT COUNT(*) FROM medals WHERE medaltype = 'GOLD'")
q("SELECT COUNT(country) FROM medals WHERE country = 'CANADA'")"""),
        md("## 🧪 DISTINCT — unique values in a column"),
        code("""q("SELECT country FROM medals")   # with duplicates
q("SELECT DISTINCT country FROM medals")   # each country once
q("SELECT DISTINCT country FROM medals WHERE medaltype = 'GOLD'")"""),
        md("## 🧪 LIMIT — restrict how many rows come back"),
        code("""q("SELECT * FROM medals LIMIT 5")
q("SELECT * FROM medals WHERE year = 2018 LIMIT 3")"""),
        md("## 🧪 Combine all three: distinct gold countries + their counts"),
        code("q(\"SELECT DISTINCT country FROM medals WHERE medaltype = 'GOLD' ORDER BY country LIMIT 4\")"),
        md("""## 💡 Tips & tricks

- **Explore with LIMIT, not SELECT *** — on millions of rows, LIMIT answers almost
  instantly; SELECT * walks the whole table through the wire.
- 📕 Dialect note: `LIMIT 10` (SQLite/MySQL/Postgres) = `TOP 10` (SQL Server) =
  `FETCH FIRST 10 ROWS ONLY` (DB2/Oracle 12c+).

## 🎯 Your turn

1. How many medals did the UK win in total? In gold?
2. The list of medal *types* awarded in 2018 (each once)."""),
        code("""# 💡 Solution
q("SELECT COUNT(*) AS uk_total FROM medals WHERE country = 'UK'")
q("SELECT COUNT(*) AS uk_gold FROM medals WHERE country = 'UK' AND medaltype = 'GOLD'")
q("SELECT DISTINCT medaltype FROM medals WHERE year = 2018")"""),
    ]

def nb10():
    return [
        _intro("10", "UPDATE & DELETE", "3 — DML", "10-update-and-delete.md",
               ["write UPDATE … SET … WHERE and DELETE FROM … WHERE",
                "run the golden safety rule: preview the WHERE as a SELECT first",
                "see what a missing WHERE does — safely, inside a transaction"]),
        code(SETUP_SQL),
        md("## 🧪 The AUTHOR table + step 1: always preview"),
        code("""q("CREATE TABLE author (author_id TEXT PRIMARY KEY, lastname TEXT, firstname TEXT, email TEXT, city TEXT, country TEXT)")
q(\"\"\"
INSERT INTO author VALUES
    ('A1','Chong','Raul','RFC@ca.ibm.com','Toronto','CA'),
    ('A2','Ahuja','Rav','RA@ca.ibm.com','Markham','CA'),
    ('A3','Katta','Lakshmi','LK@in.ibm.com','Bengaluru','IN')
\"\"\")
q("SELECT * FROM author WHERE author_id = 'A2'")   # the rows UPDATE will touch
"""),
        md("## 🧪 UPDATE — change firstname/lastname of author 'A2' (course example)"),
        code("""q("UPDATE author SET lastname = 'Katta', firstname = 'Lakshmi' WHERE author_id = 'A2'")
q("SELECT * FROM author")"""),
        md("## 🧪 DELETE — remove the rows for 'A2' and 'A3' (course example)"),
        code("""q("SELECT * FROM author WHERE author_id IN ('A2','A3')")   # preview first
q("DELETE FROM author WHERE author_id IN ('A2','A3')")
q("SELECT * FROM author")"""),
        md("""## 🧪 The missing-WHERE disaster — demonstrated *safely*

A WHERE-less UPDATE hits **every row**. Inside a transaction we can watch it and Roll Back:"""),
        code("""q("INSERT INTO author VALUES ('A2','Ahuja','Rav','RA@ca.ibm.com','Markham','CA')")   # A1 never left
conn.commit()                                  # close the implicit write-txn before an explicit BEGIN
q("BEGIN")                                     # open a transaction (lecture 29)
q("UPDATE author SET firstname = 'Oops', lastname = 'Oops'")   # no WHERE!
q("SELECT * FROM author")                      # every row changed
conn.rollback()                                # undo everything
print('--- after rollback ---')
q("SELECT * FROM author")"""),
        md("""## 💡 Tips & tricks (the golden safety rules)

1. Write the **WHERE clause first**, before the UPDATE/DELETE body.
2. Run the same WHERE as a **SELECT** to preview the target rows.
3. Only then convert to UPDATE/DELETE — preferably inside a transaction.
4. DELETE (DML) removes rows; TRUNCATE (DDL, nb 06) empties a table faster.

## 🎯 Your turn

1. UPDATE all authors' city — but *safely*: begin a transaction, view the damage, roll back.
2. DELETE an author by id, previewed and verified."""),
        code("""# 💡 Solution
q("BEGIN")
q("UPDATE author SET city = 'Nowhere'")
q("SELECT * FROM author")
conn.rollback()
q("SELECT * FROM author")

q("SELECT * FROM author WHERE author_id = 'A2'")     # preview
q("DELETE FROM author WHERE author_id = 'A2'")
q("SELECT * FROM author")"""),
    ]

def build():
    import builder
    nbs = {}
    for name, fn in [
        ("00-START-HERE", nb00), ("01-course-welcome-and-overview", nb01),
        ("02-sql-databases-and-rdbms", nb02), ("03-types-of-sql-statements-ddl-vs-dml", nb03),
        ("04-database-concepts-relational-model", nb04), ("05-create-table", nb05),
        ("06-alter-drop-and-truncate", nb06), ("07-insert-statement", nb07),
        ("08-select-statement-where-clause", nb08), ("09-count-distinct-limit", nb09),
        ("10-update-and-delete", nb10),
    ]:
        nbs[name] = builder.make_notebook(fn())
    return nbs