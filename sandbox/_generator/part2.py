"""Notebook content for lectures 11-20."""
from builder import SETUP_SQL, code, md

def _intro(no, title, module, src, goals):
    g = "\n".join(f"- {x}" for x in goals)
    return md(f"""# {no}. {title}

*Module: {module} · Companion summary: `lectures/{src}` · SQL engine: SQLite (in-memory)*

## What you will study

{g}

---
## Setup — build the sample database this notebook runs on
*Run the cell below first: it creates an in-memory SQLite database and the `q()` helper that prints every query's result set.*""")

_BOOK = """q("CREATE TABLE book (book_id TEXT PRIMARY KEY, title TEXT, pages INTEGER, year INTEGER)")
q(\"\"\"
INSERT INTO book VALUES
    ('B1', 'The Little Prince',   292, 1943),
    ('B2', 'Journey to the West', 298, 1592),
    ('B3', 'SQL Basics',          150, 2018),
    ('B4', 'Data Science Handbook', 400, 2020),
    ('B5', 'A Short Story',        45, 2022)
\"\"\")
q("SELECT * FROM book")"""

def nb11():
    return [
        _intro("11", "LIKE · BETWEEN · IN", "4 — Advanced querying", "11-like-between-in.md",
            ["find patterns with LIKE and the three wildcard positions",
             "treat LIKE's case sensitivity correctly in SQLite",
             "filter numeric ranges with BETWEEN",
             "filter lists of values with IN"]),
        code(SETUP_SQL),
        md("## 🧪 Sample data — BOOK"),
        code(_BOOK),
        md("## 🧪 LIKE — pattern matching with % (any run of characters)"),
        code("""q("SELECT title FROM book WHERE title LIKE '%Prince%'")   # contains
q("SELECT title FROM book WHERE title LIKE 'The%'")   # starts with
q("SELECT title FROM book WHERE title LIKE '%Prince'")   # ends with
q("SELECT title FROM book WHERE title LIKE '%Story%'")   # contains, later case
"""),
        md("## 🧪 The second wildcard _ — exactly ONE character"),
        code("q(\"SELECT title FROM book WHERE title LIKE '_ Short%'\")   # 'A Short Story'"),
        md("""## 🧪 LIKE + functions — case is something YOU control

SQLite's LIKE is case-insensitive for ASCII by default (MySQL too; DB2 is
case-sensitive), but the reliable habit is to normalize with UPPER()/LOWER()
*or* rely on SQLite's builtin — see both:"""),
        code("""q("SELECT title FROM book WHERE UPPER(title) LIKE '%LITTLE%'")   # explicit normalization
q("SELECT title FROM book WHERE title LIKE '%little%'")   # SQLite default: matches too
"""),
        md("## 🧪 BETWEEN — inclusive numeric range"),
        code("q(\"SELECT title, pages FROM book WHERE pages BETWEEN 290 AND 300\")\nq(\"SELECT title, pages FROM book WHERE pages BETWEEN 150 AND 292\")   # boundaries included"),
        md("## 🧪 IN — membership in a list"),
        code("q(\"SELECT title FROM book WHERE book_id IN ('B1', 'B3', 'B5')\")\nq(\"SELECT title FROM book WHERE year IN (1943, 1592, 2020)\")"),
        md("""## 💡 Tips & tricks

- `%` = any string (even empty), `_` = exactly one character — practice until instant.
- NOT LIKE / NOT BETWEEN / NOT IN all exist and read naturally.
- 📕 Dialect note: DB2/Oracle spell `BETWEEN ... AND` the same; for case-insensitive
  matching everywhere, always write `WHERE LOWER(col) LIKE '%x%'`.

## 🎯 Your turn

1. All titles containing the word 'the' (any position).
2. Books of 100–200 pages, using BETWEEN.
3. Titles of books NOT in years 2018 and 2020 (use NOT IN)."""),
        code("""# 💡 Solution
q("SELECT title FROM book WHERE title LIKE '%the%'")
q("SELECT title FROM book WHERE pages BETWEEN 100 AND 200")
q("SELECT title FROM book WHERE year NOT IN (2018, 2020)")"""),
    ]

def nb12():
    return [
        _intro("12", "ORDER BY", "4 — Advanced querying", "12-order-by.md",
            ["sort result rows ascending and descending",
             "sort by column position and by multiple columns",
             "combine ORDER BY with LIMIT for a Top-N query"]),
        code(SETUP_SQL),
        md("## 🧪 Sample data — BOOK"),
        code(_BOOK),
        md("## 🧪 ORDER BY — ascending is the default"),
        code("q(\"SELECT title, pages FROM book ORDER BY pages\")"),
        md("## 🧪 DESC — descending"),
        code("q(\"SELECT title, pages FROM book ORDER BY pages DESC\")"),
        md("## 🧪 Positional ORDER BY — '2' means the 2nd column of the SELECT list"),
        code("q(\"SELECT title, pages FROM book ORDER BY 2 DESC\")"),
        md("## 🧪 Multiple columns — secondary sort key"),
        code("""q("SELECT title, year, pages FROM book ORDER BY year DESC, pages ASC")
q("SELECT title, year, pages FROM book ORDER BY 2, 3")"""),
        md("## 🧪 Top-N — the classic ORDER BY + LIMIT combo"),
        code("q(\"SELECT title, pages FROM book ORDER BY pages DESC LIMIT 3\")"),
        md("""## 💡 Tips & tricks

- ORDER BY runs *after* the rows are selected — it's presentation, not filtering.
- Prefer naming columns over positional ORDER BY (readability), but know the position
  form for reading other people's code.
- 📕 Dialect note: identical on all engines; SQL Server uses `TOP`/`OFFSET…FETCH`
  syntaxes but ORDER BY itself is universal.

## 🎯 Your turn

1. The 2 oldest books (smallest years), newest-first sorted... careful: sort descending
   by year and take the 2 **newest**; then sort ascending and take 2 **oldest**.
2. Alphabetical list of titles, Z→A."""),
        code("""# 💡 Solution
q("SELECT title, year FROM book ORDER BY year DESC LIMIT 2")   # 2 newest
q("SELECT title, year FROM book ORDER BY year ASC LIMIT 2")   # 2 oldest
q("SELECT title FROM book ORDER BY title DESC")"""),
    ]

def nb13():
    return [
        _intro("13", "GROUP BY · HAVING · AS", "4 — Advanced querying",
               "13-group-by-having-as.md",
            ["remove duplicates with DISTINCT",
             "summarize groups of rows with GROUP BY",
             "filter groups with HAVING — and know why WHERE can't",
             "rename output columns with AS"]),
        code(SETUP_SQL),
        md("""## 🧪 Sample data — 20 authors, 6 countries

Watch how the same data looks raw → distinct → grouped → filtered:"""),
        code("""q("CREATE TABLE author (author_id TEXT PRIMARY KEY, lastname TEXT, firstname TEXT, email TEXT, country TEXT)")
q(\"\"\"
INSERT INTO author VALUES
    ('A1','Chong','Raul','RFC@ca.ibm.com','CA'),
    ('A2','Ahuja','Rav','RA@ca.ibm.com','CA'),
    ('A3','Smith','Jack','JS@ca.ibm.com','CA'),
    ('A4','Sharma','Priya','PS@in.ibm.com','IN'),
    ('A5','Patel','Arjun','AP@in.ibm.com','IN'),
    ('A6','Gupta','Neha','NG@in.ibm.com','IN'),
    ('A7','Singh','Rahul',null,'IN'),
    ('A8','Verma','Kavya',null,'IN'),
    ('A9','Reddy','Anil',null,'IN'),
    ('A10','Wang','Wei','WW@cn.ibm.com','CN'),
    ('A11','Li','Ming','LM@cn.ibm.com','CN'),
    ('A12','Zhang','Yu','ZY@cn.ibm.com','CN'),
    ('A13','Liu','Chen',null,'CN'),
    ('A14','Chen','Xiao',null,'CN'),
    ('A15','Zhao','Feng',null,'CN'),
    ('A16','Miller','Dana','DM@us.ibm.com','US'),
    ('A17','Wilson','Kate','KW@us.ibm.com','US'),
    ('A18','Silva','Ana','AS@br.ibm.com','BR'),
    ('A19','Costa','Joao','JC@br.ibm.com','BR'),
    ('A20','Brown','Emma','EB@au.ibm.com','AU')
\"\"\")
q("SELECT country FROM author")   # 20 rows, full of duplicates
"""),
        md("## 🧪 Step 1 — DISTINCT: collapse the duplicates"),
        code("q(\"SELECT DISTINCT country FROM author\")"),
        md("## 🧪 Step 2 — GROUP BY + COUNT: *how many* per country"),
        code("q(\"SELECT country, COUNT(*) AS \\\"Count\\\" FROM author GROUP BY country ORDER BY 2 DESC\")"),
        md("## 🧪 Step 3 — HAVING: filter the GROUPS (not the rows)"),
        code("q(\"SELECT country, COUNT(*) AS \\\"Count\\\" FROM author GROUP BY country HAVING COUNT(*) > 4\")"),
        md("## 🧪 Why WHERE can't do this — read the error"),
        code("""# WHERE runs BEFORE grouping; aggregates aren't computed yet → error:
# SELECT country, COUNT(*) FROM author WHERE COUNT(*) > 4 GROUP BY country"""),
        code("""import sqlite3
try:
    conn.execute("SELECT country, COUNT(*) FROM author WHERE COUNT(*) > 4 GROUP BY country")
except sqlite3.OperationalError as e:
    print(repr(e))   # misuse of aggregate: WHERE filters pre-grouping rows"""),
        md("## 🧪 COUNT(*) vs COUNT(column) — NULLs matter"),
        code("q(\"SELECT COUNT(*) AS all_rows, COUNT(email) AS with_email FROM author\")"),
        md("""## 💡 Tips & tricks

- Every column in SELECT must be either in GROUP BY or inside an aggregate.
- HAVING ≈ "a WHERE that runs after grouping" — aggregates allowed inside.
- 📕 Dialect note: quoting an alias with double quotes works everywhere ("Count");
  SQLite is fine with it; SQL Server uses `[]` brackets instead.

## 🎯 Your turn

1. Countries with fewer than 3 authors.
2. Distinct first names, then count authors per first name, largest groups first."""),
        code("""# 💡 Solution
q("SELECT country, COUNT(*) FROM author GROUP BY country HAVING COUNT(*) < 3")
q("SELECT DISTINCT firstname FROM author")
q("SELECT firstname, COUNT(*) AS n FROM author GROUP BY firstname ORDER BY n DESC")"""),
    ]

def nb14():
    return [
        _intro("14", "Built-in SQL Functions", "4 — Advanced querying",
               "14-builtin-sql-functions.md",
            ["aggregate functions: SUM, MIN, MAX, AVG, COUNT",
             "scalar (string) functions: ROUND, LENGTH, UPPER, LOWER",
             "combine them: scalar inside aggregate, functions in WHERE and SELECT"]),
        code(SETUP_SQL),
        md("""## 🧪 Sample data — PETRESCUE (animal rescue records)

Columns: rescue id, animal, quantity rescued, cost of rescue, date."""),
        code("""q("CREATE TABLE petrescue (id INTEGER PRIMARY KEY, animal TEXT, quantity INTEGER, cost REAL, rescue_date TEXT)")
q(\"\"\"
INSERT INTO petrescue VALUES
    (1, 'Dog',   1, 100.0, '2018-05-01'),
    (2, 'Cat',   1,  50.0, '2018-05-10'),
    (3, 'Dog',   2, 120.0, '2018-06-15'),
    (4, 'Bird',  3,  60.0, '2019-05-02'),
    (5, 'Cat',   2,  80.0, '2019-06-20'),
    (6, 'Dog',   1, 150.0, '2020-01-05'),
    (7, 'Bird',  5,  75.0, '2020-02-14'),
    (8, 'Cat',   1,  45.0, '2020-05-30')
\"\"\")
q("SELECT * FROM petrescue")"""),
        md("## 🧪 SUM — and rename the output with AS"),
        code("q(\"SELECT SUM(cost) AS total_cost FROM petrescue\")"),
        md("## 🧪 MIN / MAX — with and without WHERE"),
        code("""q("SELECT MIN(cost) FROM petrescue")
q("SELECT MIN(cost) FROM petrescue WHERE animal = 'Dog'")
q("SELECT MAX(cost) FROM petrescue")
q("SELECT MAX(cost) FROM petrescue WHERE animal = 'Dog'")"""),
        md("## 🧪 AVG — and nesting a scalar function inside it"),
        code("q(\"SELECT AVG(cost) FROM petrescue\")\nq(\"SELECT ROUND(AVG(cost), 2) AS avg_cost FROM petrescue WHERE animal = 'Dog'\")\nq(\"SELECT ROUND(AVG(cost / quantity), 2) AS avg_cost_per_animal FROM petrescue WHERE animal = 'Dog'\")"),
        md("## 🧪 Scalar functions change values row by row"),
        code("q(\"SELECT animal, UPPER(animal) AS up, LOWER(animal) AS low, LENGTH(animal) AS len FROM petrescue\")"),
        md("## 🧪 Scalar functions as WHERE predicates"),
        code("""q("SELECT id, animal, cost FROM petrescue WHERE LOWER(animal) = 'dog'")
q("SELECT id, animal FROM petrescue WHERE LENGTH(animal) = 4")"""),
        md("## 🧪 Nesting: DISTINCT(UPPER(...)) — dedupe after transforming"),
        code("q(\"SELECT DISTINCT(UPPER(animal)) AS animal_type FROM petrescue\")"),
        md("""## 💡 Tips & tricks

- **Aggregate** functions collapse many rows → one value; **scalar** functions map
  one row → one value. Saying the distinction out loud fixes it in memory.
- ROUND(x, n) exists in SQLite and DB2; check your engine's list before assuming.
- 📕 Dialect note: DB2 has `TRUNCATE`-like `TRUNC`, Oracle `RPAD/LPAD` etc.; SQLite's
  built-ins are leaner — most string manipulation is often better done in pandas.

## 🎯 Your turn

1. Total cost of rescuing birds.
2. The average quantity per rescue, rounded to 1 decimal.
3. Distinct animals in lowercase."""),
        code("""# 💡 Solution
q("SELECT SUM(cost) FROM petrescue WHERE animal = 'Bird'")
q("SELECT ROUND(AVG(quantity), 1) FROM petrescue")
q("SELECT DISTINCT(LOWER(animal)) FROM petrescue")"""),
    ]

def nb15():
    return [
        _intro("15", "Date & Time Functions", "4 — Advanced querying",
               "15-date-and-time-functions.md",
            ["extract parts of a date (day, month, year)",
             "count rows per month / per year",
             "do date arithmetic and measure day differences",
            "know the dialect traps: DAY()/MONTH()/CURRENT DATE vs SQLite's strftime"]),
        code(SETUP_SQL),
        md("## 🧪 Sample data — PETRESCUE again (dates this time)"),
        code("""q("CREATE TABLE petrescue (id INTEGER PRIMARY KEY, animal TEXT, quantity INTEGER, cost REAL, rescue_date TEXT)")
q(\"\"\"
INSERT INTO petrescue VALUES
    (1, 'Dog',   1, 100.0, '2018-05-01'),
    (2, 'Cat',   1,  50.0, '2018-05-10'),
    (3, 'Dog',   2, 120.0, '2018-06-15'),
    (4, 'Bird',  3,  60.0, '2019-05-02'),
    (5, 'Cat',   2,  80.0, '2019-06-20'),
    (6, 'Dog',   1, 150.0, '2020-01-05'),
    (7, 'Bird',  5,  75.0, '2020-02-14'),
    (8, 'Cat',   1,  45.0, '2020-05-30')
\"\"\")
q("SELECT * FROM petrescue")"""),
        md("""## 🧪 Extract parts of a date

📕 The course uses DB2: `DAY(rescue_date)`, `MONTH(rescue_date)`, `YEAR(rescue_date)`.
SQLite spells the same idea with **strftime**:"""),
        code("""q("SELECT rescue_date, strftime('%d', rescue_date) AS day, strftime('%m', rescue_date) AS month, strftime('%Y', rescue_date) AS year FROM petrescue")"""),
        md("## 🧪 Count rescues in a given month"),
        code("q(\"SELECT COUNT(*) FROM petrescue WHERE strftime('%m', rescue_date) = '05'\")\nq(\"SELECT COUNT(*) FROM petrescue WHERE strftime('%Y', rescue_date) = '2020'\")"),
        md("## 🧪 Date arithmetic — DATE(date, modifier)"),
        code("""q("SELECT id, rescue_date, DATE(rescue_date, '+3 day') AS three_days_later FROM petrescue LIMIT 3")
q("SELECT id, rescue_date, DATE(rescue_date, '-1 month') AS week_before FROM petrescue LIMIT 3")"""),
        md("## 🧪 Day difference with JULIANDAY"),
        code("q(\"SELECT id, rescue_date, CAST(julianday('2020-12-31') - julianday(rescue_date) AS INTEGER) AS days_to_year_end FROM petrescue LIMIT 4\")"),
        md("## 🧪 Today"),
        code("q(\"SELECT date('now') AS today\")"),
        md("""## 💡 Tips & tricks

- SQLite stores dates best as **TEXT in ISO format** (`YYYY-MM-DD`); lexicographic
  order = chronological order, so comparisons and sorting just work.
- 📕 Dialect cheat sheet:
  | Idea | DB2 (course) | SQLite | MySQL |
  |---|---|---|---|
  | month part | `MONTH(d)` | `strftime('%m', d)` | `MONTH(d)` |
  | add 3 days | `d + 3 DAYS` | `DATE(d, '+3 day')` | `DATE_ADD(d, INTERVAL 3 DAY)` |
  | today | `CURRENT DATE` | `date('now')` | `CURRENT_DATE` |

## 🎯 Your turn

1. How many rescues happened in May of 2019?
2. Each rescue's date shifted back 10 days.
3. Number of years since the oldest rescue."""),
        code("""# 💡 Solution
q("SELECT COUNT(*) FROM petrescue WHERE strftime('%m', rescue_date) = '05' AND strftime('%Y', rescue_date) = '2019'")
q("SELECT id, rescue_date, DATE(rescue_date, '-10 day') FROM petrescue LIMIT 4")
q("SELECT (strftime('%Y', 'now') - strftime('%Y', (SELECT MIN(rescue_date) FROM petrescue))) AS years_since")"""),
    ]

def nb16():
    return [
        _intro("16", "Sub-queries", "5 — Multi-table", "16-sub-queries.md",
            ["nest a SELECT inside the WHERE clause to avoid manual lookups",
             "use a sub-query as a column expression",
             "use a sub-query as a derived table in FROM"]),
        code(SETUP_SQL),
        md("## 🧪 Sample data — EMPLOYEE (id, first, last, salary)"),
        code("""q("CREATE TABLE employee (emp_id TEXT PRIMARY KEY, f_name TEXT, l_name TEXT, salary REAL)")
q(\"\"\"
INSERT INTO employee VALUES
    ('E1','Raul','Chong',95000),
    ('E2','Rav','Ahuja',75000),
    ('E3','Lakshmi','Katta',85000),
    ('E4','Wei','Chen',60000),
    ('E5','Ana','Silva',78000),
    ('E6','Jack','Smith',55000)
\"\"\")
q("SELECT * FROM employee")"""),
        md("""## 🧪 The problem: “who earns more than the average salary?”

The two-step manual version (run one query, read 74666.67, paste it):"""),
        code("q(\"SELECT ROUND(AVG(salary), 2) AS avg_salary FROM employee\")"),
        code("q(\"SELECT f_name, l_name, salary FROM employee WHERE salary > 74666.67\")"),
        md("""## 🧪 Sub-query in WHERE: one self-contained statement

The inner query runs first; its single value replaces the pasted number:"""),
        code("q(\"\"\"\nSELECT f_name, l_name, salary\nFROM employee\nWHERE salary > (SELECT AVG(salary) FROM employee)\n\"\"\")"),
        md("## 🧪 What breaks: an aggregate directly in WHERE (no nesting)"),
        code("""# SELECT f_name, salary FROM employee WHERE salary > AVG(salary)   # ❌"""),
        code("""import sqlite3
try:
    conn.execute("SELECT f_name, salary FROM employee WHERE salary > AVG(salary)")
except sqlite3.OperationalError as e:
    print(repr(e))   # aggregates can't appear in WHERE — they need the inner query"""),
        md("## 🧪 Sub-query as a column expression — show the average beside each row"),
        code("""q(\"\"\"
SELECT f_name, l_name, salary,
       (SELECT ROUND(AVG(salary), 2) FROM employee) AS avg_company_salary
FROM employee
\"\"\")"""),
        md("## 🧪 Sub-query as a derived table — compute in FROM, filter outside"),
        code("""q(\"\"\"
SELECT avg_sal
FROM (SELECT ROUND(AVG(salary), 2) AS avg_sal FROM employee) AS avg_table
WHERE avg_sal > 70000
\"\"\")"""),
        md("""## 💡 Tips & tricks

- Rule of thumb: the inner query must return **one value** for WHERE/column use, or a
  **temporary result set** (with an alias!) for FROM use.
- The derived-table alias (`AS avg_table`) is mandatory in most engines.

## 🎯 Your turn

1. Employees earning **less than half the max** salary (one statement, no pasted numbers).
2. Show each employee's salary and the max salary as two expression sub-queries."""),
        code("""# 💡 Solution
q("SELECT f_name, salary FROM employee WHERE salary < (SELECT MAX(salary) FROM employee) / 2")
q("SELECT f_name, salary, (SELECT MAX(salary) FROM employee) AS max_sal, (SELECT MIN(salary) FROM employee) AS min_sal FROM employee LIMIT 4")"""),
    ]

def nb17():
    return [
        _intro("17", "Working with Multiple Tables", "5 — Multi-table",
               "17-working-with-multiple-tables.md",
            ["filter with an IN (sub-query) across two tables",
             "answer the same question with a join instead — and compare",
             "see what a Cartesian product really produces",
             "write an implicit join with table aliases"]),
        code(SETUP_SQL),
        md("## 🧪 Sample data — EMPLOYEE + DEPARTMENT (the course's pair)"),
        code("""q("CREATE TABLE emp (emp_id TEXT PRIMARY KEY, f_name TEXT, l_name TEXT, salary REAL, dep_id TEXT)")
q(\"\"\"
INSERT INTO emp VALUES
    ('E1','Raul','Chong',95000,'D11'),
    ('E2','Rav','Ahuja',75000,'D11'),
    ('E3','Lakshmi','Katta',85000,'D20'),
    ('E4','Wei','Chen',60000,'D20'),
    ('E5','Ana','Silva',68000,'D30'),
    ('E6','Jack','Smith',55000,'D30')
\"\"\")
q("CREATE TABLE dept (dep_id TEXT PRIMARY KEY, dep_name TEXT, manager_id TEXT NOT NULL, loc_id TEXT)")
q(\"\"\"
INSERT INTO dept VALUES
    ('D11','IT',30001,'L0001'),
    ('D20','HR',30002,'L0002'),
    ('D30','Sales',30003,'L0001')
\"\"\")
q("SELECT * FROM emp")
q("SELECT * FROM dept")"""),
        md("""## 🧪 IN with an inner query — two-table lookup without a join

Employees who work in a department *located at L0002* — the sub-query turns the
departments table into a list of dep_ids:"""),
        code("q(\"SELECT f_name, l_name, dep_id FROM emp WHERE dep_id IN (SELECT dep_id FROM dept WHERE loc_id = 'L0002')\")"),
        md("## 🧪 Same question, reversed — via join (lecture 18 preview)"),
        code("q(\"SELECT e.f_name, e.l_name, d.loc_id FROM emp e JOIN dept d ON e.dep_id = d.dep_id WHERE d.loc_id = 'L0002'\")"),
        md("## 🧪 “Who earns more than 70000?” — sub-query in the other direction"),
        code("q(\"SELECT dep_name FROM dept WHERE dep_id IN (SELECT dep_id FROM emp WHERE salary > 70000)\")"),
        md("## 🧪 Cartesian product — FORGETTING the join condition"),
        code("""q("SELECT COUNT(*) FROM emp")
q("SELECT COUNT(*) FROM dept")
q("SELECT COUNT(*) FROM emp, dept")   # 6 x 3 = 18: every row pairs with every row
"""),
        md("## 🧪 The fix — implicit join (comma syntax + WHERE), with aliases"),
        code("""q(\"\"\"
SELECT e.f_name, e.l_name, e.salary, d.dep_name, d.loc_id
FROM emp e, dept d
WHERE e.dep_id = d.dep_id
\"\"\")"""),
        md("""## 💡 Tips & tricks

- Two tables, one FROM = Cartesian product **until** a WHERE matches keys — the classic
  accidental-row-explosion bug.
- Aliases (`emp e`) aren't just shorter: with the same table joined twice they're
  required (self-join).
- Same query, 2 spellings: `A, B WHERE keys match` ≈ `A JOIN B ON keys match` — the
  explicit JOIN is preferred (modern engines optimize both, but clarity wins).

## 🎯 Your turn

1. Department names of employees earning **less than 70000** (IN sub-query).
2. Same via the implicit-join spelling.
3. What's the Cartesian count for emp × emp (self-product)? Predict, then run."""),
        code("""# 💡 Solution
q("SELECT dep_name FROM dept WHERE dep_id IN (SELECT dep_id FROM emp WHERE salary < 70000)")
q("SELECT DISTINCT d.dep_name FROM emp e, dept d WHERE e.dep_id = d.dep_id AND e.salary < 70000")
q("SELECT COUNT(*) AS cartesian FROM emp a, emp b")"""),
    ]

def nb18():
    return [
        _intro("18", "JOIN Overview", "5 — Multi-table", "18-join-overview.md",
            ["build the borrower ⟕ loan ⟕ copy chain from the course",
             "connect entities through primary/foreign keys",
             "traverse three tables in one query"]),
        code(SETUP_SQL),
        md("""## 🧪 Sample data — a tiny library

Three entities linked by keys: BORROWER ←(1:N)— LOAN —(N:1)→ COPY —(N:1)→ BOOK"""),
        code("""q(\"\"\"
CREATE TABLE book (book_id TEXT PRIMARY KEY, title TEXT, pages INTEGER)
\"\"\")
q(\"\"\"
INSERT INTO book VALUES
    ('B1','The Little Prince', 292),
    ('B2','Journey to the West', 298),
    ('B3','SQL Basics', 150)
\"\"\")
q(\"\"\"
CREATE TABLE copy (
    copy_id TEXT PRIMARY KEY,           -- physical copy of a book
    book_id TEXT REFERENCES book(book_id)
)
\"\"\")
q(\"\"\"
INSERT INTO copy VALUES
    ('C1','B1'), ('C2','B1'), ('C3','B2'), ('C4','B3')
\"\"\")
q(\"\"\"
CREATE TABLE borrower (borrower_id TEXT PRIMARY KEY, lastname TEXT, country TEXT)
\"\"\")
q(\"\"\"
INSERT INTO borrower VALUES
    ('BR1','Smith','CA'), ('BR2','Ali','IN'), ('BR3','Lee','CN'),
    ('BR4','Peters','US'), ('BR5','Li','CN'), ('BR6','Wong','CA')
\"\"\")
q(\"\"\"
CREATE TABLE loan (
    borrower_id TEXT REFERENCES borrower(borrower_id),
    copy_id TEXT REFERENCES copy(copy_id),
    loan_date TEXT
)
\"\"\")
q(\"\"\"
INSERT INTO loan VALUES
    ('BR1','C1','2024-01-10'), ('BR1','C2','2024-02-01'),
    ('BR2','C3','2024-03-05'), ('BR3','C4','2024-04-01')
\"\"\")
q("SELECT * FROM book")
q("SELECT * FROM copy")
q("SELECT * FROM borrower")
q("SELECT * FROM loan")"""),
        md("""## 🧪 The mental model

A **join** glues tables together by matching key values. The chain for
“who borrowed what”: `borrower → loan → copy → book`, each hop on the shared key."""),
        md("## 🧪 Two hops: lender ⟕ copy"),
        code("q(\"SELECT b.lastname, l.loan_date, c.copy_id FROM borrower b JOIN loan l ON b.borrower_id = l.borrower_id JOIN copy c ON l.copy_id = c.copy_id\")"),
        md("## 🧪 The full three-table traversal"),
        code("q(\"\"\"\nSELECT b.lastname, bk.title, l.loan_date\nFROM borrower b\nJOIN loan l ON b.borrower_id = l.borrower_id\nJOIN copy c ON l.copy_id = c.copy_id\nJOIN book bk ON c.book_id = bk.book_id\n\"\"\")"),
        md("""## 💡 Tips & tricks

- Count your hops: N tables = N−1 join conditions (two forgetting hops = Cartesian
  explosion, nb17).
- Copy entities (physical items) are distinct from catalog entities (books) — a model
  pattern worth remembering.
- 📕 Dialect note: nothing dialect-specific in the join syntax — this is portable SQL.

## 🎯 Your turn

1. Which copy of JOURNEY TO THE WEST is on loan, and to whom?
2. How many loans does each borrower have (group the join result)."""),
        code("""# 💡 Solution
q(\"\"\"
SELECT c.copy_id, b.lastname
FROM copy c JOIN book bk ON c.book_id = bk.book_id
JOIN loan l ON l.copy_id = c.copy_id
JOIN borrower b ON b.borrower_id = l.borrower_id
WHERE bk.title = 'Journey to the West'
\"\"\")
q(\"\"\"
SELECT b.lastname, COUNT(*) AS n_loans
FROM borrower b JOIN loan l ON b.borrower_id = l.borrower_id
GROUP BY b.lastname
\"\"\")"""),
    ]

def nb19():
    return [
        _intro("19", "INNER JOIN", "5 — Multi-table", "19-inner-join.md",
            ["define INNER JOIN and what it keeps/drops",
             "see the fan-out effect of one-to-many matches",
             "spot the rows an INNER JOIN silently loses"]),
        code(SETUP_SQL),
        md("## 🧪 Sample data — BORROWER + LOAN (same library as nb18)"),
        code("""q("CREATE TABLE borrower (borrower_id TEXT PRIMARY KEY, lastname TEXT, country TEXT)")
q("INSERT INTO borrower VALUES ('BR1','Smith','CA'), ('BR2','Ali','IN'), ('BR3','Lee','CN'), ('BR4','Peters','US'), ('BR5','Li','CN'), ('BR6','Wong','CA')")
q("CREATE TABLE loan (borrower_id TEXT REFERENCES borrower(borrower_id), copy_id TEXT, loan_date TEXT)")
q(\"\"\"
INSERT INTO loan VALUES
    ('BR1','C1','2024-01-10'), ('BR1','C2','2024-02-01'),
    ('BR2','C3','2024-03-05'), ('BR3','C4','2024-04-01')
\"\"\")
q("SELECT * FROM borrower")
q("SELECT * FROM loan")"""),
        md("""## 🧪 INNER JOIN — only matched pairs survive

Both spellings are identical in SQLite (and most engines):"""),
        code("q(\"\"\"\nSELECT b.lastname, l.copy_id, l.loan_date\nFROM borrower b\nINNER JOIN loan l ON b.borrower_id = l.borrower_id\n\"\"\")"),
        code("q(\"\"\"\nSELECT b.lastname, l.copy_id, l.loan_date\nFROM borrower b JOIN loan l ON b.borrower_id = l.borrower_id   -- INNER is optional\n\"\"\")"),
        md("""## 🧪 Two behaviors to notice

1. **Fan-out** — Smith has 2 loans, so Smith appears twice.
2. **Lost rows** — Peters, Li and Wong have no loans: they're *silently dropped*."""),
        code("""q("SELECT lastname FROM borrower")   # 6 people
q("SELECT DISTINCT b.lastname FROM borrower b JOIN loan l ON b.borrower_id = l.borrower_id")   # 3 people
"""),
        md("""## 💡 Tips & tricks

- INNER JOIN is a *filter*: any row with no match on the other side disappears.
- Count before/after joins when data completeness matters (fan-out lies about totals:
  4 result rows ≠ 4 borrowers ≠ 4 loans).
- To *find* the lost rows instead of losing them: `LEFT JOIN ... WHERE l.borrower_id
  IS NULL` — the anti-join, covered next lecture (nb20).
- 📕 Note: `JOIN … ON key = key USING(key)` / NATURAL JOIN exist but ON is the
  universal, explicit favorite.

## 🎯 Your turn

1. Borrowers and their loan dates for loans taken in 2024-02 or later (post-join WHERE).
2. Total loan count per country — fan-out included, group the joined result."""),
        code("""# 💡 Solution
q("SELECT b.lastname, l.loan_date FROM borrower b JOIN loan l ON b.borrower_id = l.borrower_id WHERE l.loan_date >= '2024-02-01'")
q("SELECT b.country, COUNT(*) AS loans FROM borrower b JOIN loan l ON b.borrower_id = l.borrower_id GROUP BY b.country")"""),
    ]

def nb20():
    return [
        _intro("20", "LEFT · RIGHT · FULL Outer Joins", "5 — Multi-table",
               "20-left-outer-join.md",
            ["keep unmatched rows from one or both sides",
             "run LEFT, RIGHT and FULL OUTER JOIN natively (SQLite ≥ 3.39)",
             "use COALESCE to label NULLs meaningfully",
            "read outer joins as data-quality detectors"]),
        code(SETUP_SQL),
        md("""## 🧪 Sample data — borrower ⟕ loan, with *deliberate* gaps

- Peters/Li/Wong: borrowers with no loans (LEFT join will surface them as NULLs).
- One loan row points at borrower 'B999' who left the library — a data-quality issue
  the RIGHT join will surface. (No FK on this table, so the orphan can exist.)"""),
        code("""q("CREATE TABLE borrower (borrower_id TEXT PRIMARY KEY, lastname TEXT, country TEXT)")
q("INSERT INTO borrower VALUES ('BR1','Smith','CA'), ('BR2','Ali','IN'), ('BR3','Lee','CN'), ('BR4','Peters','US'), ('BR5','Li','CN'), ('BR6','Wong','CA')")
q("CREATE TABLE loan (borrower_id TEXT, copy_id TEXT, loan_date TEXT)")   # no FK: orphans allowed
q(\"\"\"
INSERT INTO loan VALUES
    ('BR1','C1','2024-01-10'), ('BR1','C2','2024-02-01'),
    ('BR2','C3','2024-03-05'), ('BR3','C4','2024-04-01'),
    ('B999','C5','2024-05-01')
\"\"\")
q("SELECT * FROM borrower")
q("SELECT * FROM loan")"""),
        md("""## 🧪 LEFT OUTER JOIN — all borrowers, matched or not

SQLite fills the no-match side with NULLs:"""),
        code("q(\"\"\"\nSELECT b.lastname, l.copy_id, l.loan_date\nFROM borrower b LEFT OUTER JOIN loan l ON b.borrower_id = l.borrower_id\n\"\"\")"),
        md("## 🧪 LEFT JOIN + WHERE col IS NULL — the anti-join"),
        code("q(\"\"\"\nSELECT b.lastname\nFROM borrower b LEFT JOIN loan l ON b.borrower_id = l.borrower_id\nWHERE l.borrower_id IS NULL\n\"\"\")"),
        md("## 🧪 RIGHT OUTER JOIN — all loans, orphaned borrower surfaced"),
        code("q(\"\"\"\nSELECT COALESCE(b.lastname, '❌ unknown borrower') AS who, l.copy_id, l.loan_date\nFROM borrower b RIGHT OUTER JOIN loan l ON b.borrower_id = l.borrower_id\n\"\"\")"),
        md("""## 🧪 FULL OUTER JOIN — nobody hides

Everything from both sides: matched pairs + unmatched borrowers + the orphan loan."""),
        code("q(\"\"\"\nSELECT COALESCE(b.lastname, '❌') AS borrower, COALESCE(l.copy_id, '—') AS copy, l.loan_date\nFROM borrower b FULL OUTER JOIN loan l ON b.borrower_id = l.borrower_id\nORDER BY borrower, copy\n\"\"\")"),
        md("""## 🧪 Diagram in words

| Join | Keeps everything from | Adds NULLs for |
|---|---|---|
| INNER | both, matched only | — |
| LEFT | left table | right-table misses |
| RIGHT | right table | left-table misses |
| FULL | both | all misses |

📕 Dialect note: MySQL has **no RIGHT/FULL** — emulate FULL as
`left-query UNION right-query` (UNION removes duplicates, which is exactly the FULL
join's semantics). SQL Server and SQLite ≥ 3.39 support all natively; this notebook
runs 3.49."""),
        md("""## 💡 Tips & tricks

- Orphan rows only appear with RIGHT/FULL joins — a great data-quality scan.
- LEFT JOIN + IS NULL = SQL's anti-join — memorize this pattern.
- Always COALESCE NULLs when presenting outer-join results.

## 🎯 Your turn

1. Loans (copy + date) for borrowers with no matching record — the orphan detector.
2. LEFT join version that shows every borrower, and the count of '' rows → how many
   borrowers have no loans?"""),
        code("""# 💡 Solution
q("SELECT l.copy_id, l.loan_date FROM borrower b RIGHT JOIN loan l ON b.borrower_id = l.borrower_id WHERE b.borrower_id IS NULL")
q("SELECT COUNT(*) AS borrowers_with_no_loans FROM (SELECT b.lastname FROM borrower b LEFT JOIN loan l ON b.borrower_id = l.borrower_id WHERE l.borrower_id IS NULL)")"""),
    ]

def build():
    import builder
    names = {
        "11-like-between-in": nb11,
        "12-order-by": nb12,
        "13-group-by-having-as": nb13,
        "14-builtin-sql-functions": nb14,
        "15-date-and-time-functions": nb15,
        "16-sub-queries": nb16,
        "17-working-with-multiple-tables": nb17,
        "18-join-overview": nb18,
        "19-inner-join": nb19,
        "20-left-right-full-outer-join": nb20,
    }
    return {name: builder.make_notebook(fn()) for name, fn in names.items()}