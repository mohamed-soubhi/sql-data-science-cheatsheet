"""Notebook content for lectures 21-29."""
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

def nb21():
    return [
        _intro("21", "Python for Databases — the SQL APIs", "6 — Python access",
               "21-python-sql-apis-overview.md",
            ["name the steps of any SQL API flow (connect → cursor → execute → close)",
             "map Python's library options to their engines",
             "connect to a database from Python and run SQL"]),
        md("""## 📗 API flow (language-neutral)

1. **Import** the library (or the generic module if the engine needs a connector).
2. **Connect** — open a connection object; provide credentials/path.
3. Get a **cursor**, or pass SQL directly to connection methods.
4. **Execute** SQL — the db engine receives and runs it.
5. **Close** the connection when done.

## 📗 Which library for which engine

| Engine | Library |
|---|---|
| SQLite (built into Python) | `sqlite3` |
| MySQL | `mysql-connector-python` / `pymysql` |
| PostgreSQL | `psycopg2` / `psycopg` |
| IBM DB2 | `ibm_db` |
| Oracle | `oracledb` |
| Any engine, one interface | `sqlalchemy` / DB-API `pyodbc` |

All follow the same flow below — learn the flow once, swap libraries often."""),
        md("## 🧪 The full flow with sqlite3 — including the failure modes"),
        code("""import sqlite3

DB = ':memory:'                  # in SQLite this could be a file path instead
conn = sqlite3.connect(DB)       # 2. connect
q_cur = conn.cursor()            # 3. cursor exists (also usable via conn.*)
q_cur.execute("CREATE TABLE demo (id INTEGER PRIMARY KEY, name TEXT)")        # 4. execute
q_cur.execute("INSERT INTO demo VALUES (1, 'hello')")
rows = q_cur.execute("SELECT * FROM demo").fetchall()                        # 5. read results
print('rows:', rows)
q_cur.close()
conn.close()                     # 5. always close — even after errors (try/finally!)"""),
        md("""## 💡 Tips & tricks

- Wrap connection cleanup in `try/finally` (or a `with` block) — see nb22.
- Errors from the engine surface as **Python exceptions** (sqlite3.Error subclasses);
  reading them is a skill in itself (you'll meet several on purpose below).

## 🎯 Your turn

1. Re-run the flow but insert 2 rows and print both.
2. What happens if you call `q_cur.execute(...)` after close? Test it."""),
        code("""# 💡 Solution
conn = sqlite3.connect(':memory:')
cur = conn.cursor()
cur.execute("CREATE TABLE demo (id INTEGER PRIMARY KEY, name TEXT)")
cur.execute("INSERT INTO demo VALUES (1, 'row one')")
cur.execute("INSERT INTO demo VALUES (2, 'row two')")
print('rows:', cur.execute("SELECT * FROM demo").fetchall())
cur.close()
try:
    cur.execute("SELECT 1")
except sqlite3.ProgrammingError as e:
    print('closed-cursor error:', e)
conn.close()"""),
        code(SETUP_SQL + "\n\n# re-establish the standard helper for the next cells"),
    ]

def nb22():
    return [
        _intro("22", "DB-API: Connections & Cursors", "6 — Python access",
               "22-database-api-connections.md",
            ["walk the five DB-API steps",
             "fetch results (fetchall / fetchone), parameterize queries (? placeholders)",
             "commit vs rollback — and why closing matters",
             "use a context manager so cleanup is automatic"]),
        md("""## 🧪 Five steps against a *real file* database

Using `tempfile` so the notebook is re-runnable without leaving junk behind:"""),
        code("""import os, sqlite3, tempfile

db_dir = tempfile.mkdtemp()                            # fresh folder per run
db_path = os.path.join(db_dir, 'demo.db')
print('database file:', db_path)

conn = sqlite3.connect(db_path)                        # STEP 1-2: open
conn.execute("CREATE TABLE person (id INTEGER PRIMARY KEY, name TEXT)")   # STEP 3/4
conn.commit()                                          # STEP 4b: persist DDL/DML
conn.execute("INSERT INTO person VALUES (1, 'Raul'), (2, 'Rav')")
conn.commit()
print('on disk now:', os.listdir(db_dir))"""),
        md("## 🧪 STEP 3 — cursor + fetchall / fetchone"),
        code("""cur = conn.cursor()
print('fetchall:', cur.execute("SELECT * FROM person").fetchall())
print('fetchone:', cur.execute("SELECT * FROM person").fetchone())   # first row only
print('rowcount:', cur.execute("SELECT COUNT(*) FROM person").fetchone()[0])"""),
        md("## 🧪 Parameterized queries — the safe way to inject values"),
        code("""who = 'Rav'
print(cur.execute("SELECT * FROM person WHERE name = ?", (who,)).fetchall())"""),
        md("""🧪 executemany — bulk insert"""),
        code("""cur.executemany("INSERT INTO person VALUES (?, ?)", [(3, 'Ana'), (4, 'Jack')])
conn.commit()
print(cur.execute("SELECT * FROM person").fetchall())"""),
        md("## 🧪 Commit vs Rollback — with the real file on disk"),
        code("""try:
    conn.execute("INSERT INTO person VALUES (5, 'Ghost')")
    conn.rollback()                     # pretend we changed our mind
finally:
    pass
print('after rollback:', cur.execute("SELECT * FROM person").fetchall())
conn.execute("INSERT INTO person VALUES (5, 'Real')")
conn.commit()
print('after commit:  ', cur.execute("SELECT * FROM person").fetchall())"""),
        md("## 🧪 STEP 5 — close, and better: the context manager"),
        code("""conn.close()
print('cursor after close:', end=' ')
try:
    cur.execute("SELECT 1")
except sqlite3.ProgrammingError as e:
    print('refused,', e)

with sqlite3.connect(db_path) as c:      # commits on success, rolls back on error
    print('inside:', c.execute("SELECT COUNT(*) FROM person").fetchone()[0], 'persons')
    c.execute("INSERT INTO person VALUES (6, 'FromWith')")   # auto-committed on exit
c.close()                                # ⚠️ 'with' handles the TRANSACTION, not the connection!
probe = sqlite3.connect(db_path)         # fresh connection to verify persistence
print('file still on disk?', os.path.exists(db_path))
print('after with:', probe.execute("SELECT * FROM person WHERE id = 6").fetchall())
probe.close()                            # close it, or Windows blocks the cleanup below
os.remove(db_path); os.rmdir(db_dir)     # tidy up the temp folder"""),
        md("""## 💡 Tips & tricks

- **`?` placeholders, never f-strings** — string-building SQL is the SQL-injection bug.
- `fetchall()` for small results, `fetchone()`/iterate for big ones.
- `with connection` is the shortcut for commit/rollback — but does **not** close the
  connection; pair with try/finally or `closing()` for that.

## 🎯 Your turn

1. Create table `book (id, title)` in a new temp file, insert 3 books via executemany,
   fetchone + fetchall, then tear down the file.
2. Insert inside `with` but trigger an exception — verify the row did NOT land."""),
        code("""# 💡 Solution
import os, sqlite3, tempfile
d = tempfile.mkdtemp(); p = os.path.join(d, 'books.db')
c = sqlite3.connect(p)
with c:                                  # transaction scope: commits when the block exits
    c.execute("CREATE TABLE book (id INTEGER PRIMARY KEY, title TEXT)")
    c.executemany("INSERT INTO book VALUES (?, ?)", [(1, 'A'), (2, 'B'), (3, 'C')])
c.close()                                # 'with' did NOT close it — we do, explicitly
cur = sqlite3.connect(p)
print('fetchone:', cur.execute('SELECT * FROM book').fetchone())
print('fetchall:', cur.execute('SELECT * FROM book').fetchall())
cur.close()
os.remove(p); os.rmdir(d)                # only safe once every connection is closed

d = tempfile.mkdtemp(); p = os.path.join(d, 'rb.db')
c = sqlite3.connect(p)
try:
    with c:                                  # anything raised inside → automatic ROLLBACK
        c.execute("CREATE TABLE t (x INTEGER CHECK (x < 10))")
        c.execute("INSERT INTO t VALUES (1)")            # would be lost...
        c.execute("INSERT INTO t VALUES (99)")           # CHECK constraint fires →
        print('never reached')                           # ...because we never commit
except sqlite3.IntegrityError as e:
    print('constraint fired:', e)
c.close()                                    # with = transaction scope, NOT a close
chk = sqlite3.connect(p)
print('rows after failed txn (row 1 must be GONE):', chk.execute('SELECT * FROM t').fetchall())
chk.close()
os.remove(p); os.rmdir(d)"""),
    ]

def nb23():
    return [
        _intro("23", "SQL Magic in Jupyter", "6 — Python access",
               "23-sql-magic.md",
            ["know what SQL Magic is (line/cell magics from ipython-sql)",
             "try the magics if available, with a runnable DB-API fallback either way",
             "map magic syntax ↔ plain Python calls"]),
        md("""## 📗 SQL Magic (ipython-sql)

In the course's labs, the first cell does:
```bash
pip install ipython-sql           # (commented here — see below)
%load_ext sql
%sql sqlite://                    # connect (in-memory) — in labs: %sql ibm_db... + credentials
```
Then SQL reads like a natural language: `%sql SELECT ...` (one line) or
```
%%sql
SELECT ...
```
(a whole cell, no Python). If the optional package isn't installed in this
environment, the magics below simply print a hint and the DB-API equivalent still
runs — nothing fails."""),
        code("""# Optional: uncomment to try the real magics
# !pip install ipython-sql

try:
    ipython = get_ipython()
    ipython.run_line_magic('load_ext', 'sql')
    ipython.run_line_magic('sql', 'sqlite://')
    print('✅ SQL Magic loaded - the %%sql cells below work')
except Exception as e:
    print('ℹ️ SQL Magic unavailable here:', type(e).__name__, '-')
    print('   using plain sqlite3 (DB-API) for every query in this notebook: same SQL.')"""),
        md("## 🧪 Try a line magic (`%sql`) — or the equivalent DB-API call"),
        code("""import sqlite3           # ensure the DB-API import exists even without the magics
try:
    ipython = get_ipython()
    out = ipython.run_line_magic('sql', 'SELECT 1 AS one')
    print(out)
except Exception:
    print('%sql equivalent in pure Python:')
    print(sqlite3.connect(':memory:').execute('SELECT 1 AS one').fetchall())"""),
        md("## 🧪 A second magic for flavor: `%pwd` (built into IPython, no install needed)"),
        code("""print(get_ipython().run_line_magic('pwd', ''))"""),
        md("## 🧪 A %%sql-style cell, done in DB-API"),
        code(SETUP_SQL + """

q(\"\"\"
SELECT 'magic-free sql' AS note, 2 * 21 AS the_answer
\"\"\")"""),
        md("""## 💡 Tips & tricks

- Magics are *sugar* over the same DB-API underneath — SQL identical, ergonomics differ.
- `%sql` handles credentials in one place (labs: Cloud DB2 credential string) — that's
  its main real-world advantage in this course.
- If your `%sql` connection is to a **file**: `%%sql sqlite:///path/to/db.sqlite`.

## 🎯 Your turn

1. Write a %%sql-style multi-line query result in DB-API (any SELECT).
2. Try `get_ipython().run_line_magic('lsmagic', '')` and count line magics (just for fun)."""),
        code("""# 💡 Solution
conn = sqlite3.connect(':memory:')
conn.execute("CREATE TABLE t (a, b)")
conn.execute("INSERT INTO t VALUES (1, 'x')")
cur = conn.execute(\"\"\"
SELECT a, b FROM t WHERE b = 'x'
\"\"\")
print(cur.fetchall())

try:
    mags = get_ipython().run_line_magic('lsmagic', '').magics_manager.magics
    print('line magics available:', len(mags.get('line', {})))
except Exception as e:
    print('lsmagic introspection unavailable:', e)"""),
    ]

def nb24():
    return [
        _intro("24", "Real-world CSVs → SQL", "6 — Python access",
               "24-real-world-csv-loading.md",
            ["read a CSV with pandas and push it into SQL with to_sql",
             "load data where it isn't in a database yet",
             "handle identifiers with backticks / double quotes"]),
        md("""## 🧪 Synthesize a small `dogs.csv` (course's dataset flavor: a real-world CSV)

We write one with pandas, then do the full CSV → SQL pipeline. `tempfile` keeps
re-runs clean:"""),
        code("""import os, sqlite3, tempfile
import pandas as pd

csv_path = os.path.join(tempfile.mkdtemp(), 'dogs.csv')
df = pd.DataFrame({
    'name':   ['Max', 'Bella', 'Rocky', 'Luna'],
    'breed':  ['Labrador', 'Poodle', 'Boxer', 'Husky'],
    'age':    [5, 3, 8, 2],
    'weight_kg': [30.0, 6.5, 32.0, 26.0],
})
df.to_csv(csv_path, index=False)
print(open(csv_path).read())"""),
        md("## 🧪 read the CSV straight back with pandas"),
        code("dogs = pd.read_csv(csv_path)\ndogs"),
        md("## 🧪 push it into SQLite — read_sql_query to get it back"),
        code("""conn = sqlite3.connect(':memory:')
dogs.to_sql('dogs', conn, index=False, if_exists='replace')   # the magic line
pd.read_sql_query("SELECT * FROM dogs", conn)"""),
        md("## 🧪 ... or with our q() helper (raw sqlite3, no pandas for the result)"),
        code(SETUP_SQL + """

dogs.to_sql('dogs', conn, index=False, if_exists='replace')
q("SELECT * FROM dogs")"""),
        md("## 🧪 SQL against CSV data — LIMIT and column selection"),
        code("q(\"SELECT name, breed FROM dogs LIMIT 2\")\nq(\"SELECT name, weight_kg FROM dogs WHERE weight_kg > 25 ORDER BY weight_kg\")"),
        md("## 🧪 Identifier quoting — the course backtick story"),
        code("""# A column whose name is a reserved word needs quoting:
q('SELECT name AS \"breed name\" FROM dogs LIMIT 1')
try:
    conn.execute('SELECT name AS `my col` FROM dogs LIMIT 1').fetchall()   # backticks!
    print('SQLite accepts MySQL-style BACKTICK quoting too')
except sqlite3.OperationalError as e:
    print('backtick unsupported:', e)"""),
        md("""## 💡 Tips & tricks

- Pipeline to remember: `pd.read_csv → df.to_sql → pd.read_sql_query` (or plain
  sqlite3 for one-off queries).
- If your CSV is huge: `chunksize=...` in read_csv + chunk-wise to_sql.
- Backtick habit from the course labs (`` `my-col` ``) is **MySQL/SQLite only** —
  PostgreSQL/Oracle use `"col"`.

## 🎯 Your turn

1. Make the CSV bigger (add 2 dogs), reload it and re-query in one go.
2. Run the whole round trip for a `cats.csv` you invent."""),
        code("""# 💡 Solution
df2 = pd.concat([dogs, pd.DataFrame({'name':['Nala','Zeus'], 'breed':['Beagle','Corgi'], 'age':[4,1], 'weight_kg':[12.0,10.5]})], ignore_index=True)
d = tempfile.mkdtemp(); p = os.path.join(d, 'dogs2.csv')
df2.to_csv(p, index=False)
conn.execute('DROP TABLE IF EXISTS dogs')
pd.read_csv(p).to_sql('dogs', conn, index=False)
q("SELECT * FROM dogs")
df2.to_csv(os.path.join(tempfile.mkdtemp(), 'cats.csv'), index=False)
print('round trip for cats.csv done the same way — try it yourself with renamed columns.')"""),
    ]

def nb25():
    return [
        _intro("25", "Metadata Catalogs", "6 — Python access",
               "25-metadata-catalogs.md",
            ["ask the database *about itself* with catalog queries",
             "browse sqlite_master (SQLite's system catalog)",
             "get column-level metadata with PRAGMA table_info"]),
        code(SETUP_SQL),
        md("## 🧪 Build something to catalog — the course AUTHOR table"),
        code("""q("CREATE TABLE author (author_id TEXT PRIMARY KEY, lastname TEXT NOT NULL, firstname TEXT NOT NULL, email TEXT, city TEXT, country TEXT)")
q("INSERT INTO author VALUES ('A1', 'Chong', 'Raul', 'RFC@ca.ibm.com', 'Toronto', 'CA')")
q("CREATE TABLE book (book_id TEXT PRIMARY KEY, title TEXT, author_id TEXT REFERENCES author(author_id))")
q("INSERT INTO book VALUES ('B1', 'My Book', 'A1')")"""),
        md("## 🧪 sqlite_master — the list of every object in the database"),
        code("q(\"SELECT name, type FROM sqlite_master\")"),
        md("## 🧪 The full CREATE statement, as recorded in the catalog"),
        code("q(\"SELECT sqlite_master.sql FROM sqlite_master WHERE name = 'author'\")"),
        md("## 🧪 PRAGMA table_info — the column report"),
        code("q(\"PRAGMA table_info(author)\")"),
        md("""**Reading the columns**: `cid, name, type, notnull, dflt_value, pk` —
`author_id` has `pk: 1`; lastname/firstname have `notnull: 1`, matching the DDL."""),
        code("q(\"PRAGMA table_info(book)\")"),
        md("""## 💡 Tips & tricks

- Catalog queries are how tools and ORMs introspect a schema — and how *you* write
  schema-checking scripts (does `email` exist before migrating? now you can ask).
- 📕 Dialect note: DB2/Oracle call these SYSTEM CATALOG / SYSCAT / SYSIBM tables
  (`SYSCAT.TABLES`), MySQL has `information_schema.tables`; SQLite's lightweight
  equivalent is `sqlite_master` + PRAGMAs.
- The catalog is a *read-mostly* table: never hand-edit it; use DDL.

## 🎯 Your turn

1. List every table (type='table') excluding the ones whose name starts with
   `sqlite_` (internal).
2. Write a tiny introspector: for each user table, print its name and column count."""),
        code("""# 💡 Solution
q("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'")
for (tname,) in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"):
    n = conn.execute(f"PRAGMA table_info({tname})").fetchall()
    print(f'{tname}: {len(n)} columns')"""),
    ]

def nb26():
    return [
        _intro("26", "EDA with pandas, seaborn & SQL", "6 — Python access",
               "26-eda-with-sql-and-pandas.md",
            ["profile a dataset with SQL + pandas describe()",
             "find extreme rows with idxmax / .at",
             "draw swarmplot, jointplot, boxplot — inline in this notebook"]),
        md("""## 🧪 Build the nutrition table in memory (a McDonald's-style menu)

Twelve items across 4 categories, sodium in mg."""),
        code("""import sqlite3
import pandas as pd
conn = sqlite3.connect(':memory:')

menu = pd.DataFrame({
    'item': ['Big Mac', 'Quarter W L Cheese', 'McChicken', 'French Fries L',
             'Chicken Mc N 20pc', 'Chicken Mc N 40pc', 'Sausage Mc Muffin',
             'Egg Mc Muffin', 'Hot Caramel Sundae', 'Apple Pie',
             'Garden Salad', 'Coca-Cola M'],
    'category': ['Beef', 'Beef', 'Chicken', 'Sides',
                 'Chicken', 'Chicken', 'Breakfast', 'Breakfast',
                 'Dessert', 'Dessert', 'Sides', 'Drinks'],
    'sodium_mg': [1010, 1290, 1200, 190,
                  1500, 3600, 780, 750, 150, 180, 65, 30],
})
menu.head()"""),
        md("## 🧪 SQL for the raw table + pandas describe() for statistics"),
        code("""menu.to_sql('menu', conn, index=False, if_exists='replace')
pd.read_sql_query("SELECT category, COUNT(*) AS items, ROUND(AVG(sodium_mg),1) AS avg_sodium FROM menu GROUP BY category ORDER BY avg_sodium DESC", conn)"""),
        code("""menu[['sodium_mg']].describe()"""),
        md("## 🧪 Which item is the sodium bomb? idxmax + .at"),
        code("""row = menu['sodium_mg'].idxmax()
print('max sodium row:', row)
print(menu.at[row, 'item'], '→', menu.at[row, 'sodium_mg'], 'mg')
menu[menu.category == 'Chicken'].sort_values('sodium_mg', ascending=False)"""),
        md("## 🧪 Plots (need `matplotlib inline` in a live session)"),
        code("""import matplotlib.pyplot as plt
import seaborn as sns

# 1. swarmplot — every item's sodium, split by category
plt.figure(figsize=(7, 4))
sns.swarmplot(data=menu, x='category', y='sodium_mg', hue='category', legend=False)
plt.title('Sodium by category — swarmplot')
plt.tight_layout()
plt.show()  # displayed inline when running in Jupyter"""),
        code("""# 2. jointplot — sodium vs category index (relationship view)
plt.figure(figsize=(6, 4))
sns.jointplot(data=menu, x='sodium_mg', y='category', height=5)
plt.show()"""),
        code("""# 3. boxplot — distribution per category
plt.figure(figsize=(7, 4))
sns.boxplot(data=menu, x='category', y='sodium_mg', hue='category', legend=False)
plt.title('Sodium spread — boxplot')
plt.tight_layout()
plt.show()"""),
        md("""## 💡 Tips & tricks

- SQL for aggregation, pandas/seaborn for the visual layer — combine both (course's
  lab does exactly this).
- 3600 mg sodium in the 40-piece McNuggets: >1.5× the daily allowance — EDA makes
  such outliers unmissable (the course's point!).

## 🎯 Your turn

1. Top-3 items by sodium (SQL ORDER BY + LIMIT — or pandas `.nlargest(3)`).
2. Average sodium per category as a seaborn barplot."""),
        code("""# 💡 Solution
import pandas as pd
print(pd.read_sql_query("SELECT item, sodium_mg FROM menu ORDER BY sodium_mg DESC LIMIT 3", conn))
print(menu['sodium_mg'].nlargest(3))
plt.figure(figsize=(6, 3))
sns.barplot(data=menu, x='category', y='sodium_mg', hue='category', legend=False)
plt.title('Average sodium by category')
plt.tight_layout()
plt.show()"""),
    ]

def nb27():
    return [
        _intro("27", "Views", "7 — Advanced server", "27-views.md",
            ["create a virtual table with CREATE VIEW",
             "query a view like any table",
             "replace and drop views; honor the no-ORDER-BY-inside rule"]),
        code(SETUP_SQL),
        md("## 🧪 Sample table — EMPLOYEE with sensitive data"),
        code("""q("CREATE TABLE employee (emp_id TEXT PRIMARY KEY, f_name TEXT, l_name TEXT, salary REAL, dep_id TEXT, ssn TEXT)")
q(\"\"\"
INSERT INTO employee VALUES
    ('E1','Raul','Chong',95000,'D11','123-45-6789'),
    ('E2','Rav','Ahuja',75000,'D11','234-56-7890'),
    ('E3','Lakshmi','Katta',85000,'D20','345-67-8901')
\"\"\")
q("SELECT * FROM employee")"""),
        md("""## 🧪 CREATE VIEW — a saved SELECT (no salary, no SSN)"""),
        code("q(\"CREATE VIEW empinfo AS SELECT emp_id, f_name, l_name, dep_id FROM employee\")"),
        md("## 🧪 The view queries like a table"),
        code("q(\"SELECT * FROM empinfo\")\nq(\"SELECT f_name, dep_id FROM empinfo WHERE dep_id = 'D20'\")"),
        md("## 🧪 Views re-compute — live through the base table"),
        code("""q("INSERT INTO employee VALUES ('E4','Ana','Silva',68000,'D30','456-78-9012')")
q("SELECT * FROM empinfo")   # Ana appears, although she wasn't there at CREATE time
"""),
        md("""## 🧪 Replace a view

SQLite has no `CREATE OR REPLACE VIEW` — the portable recipe is drop + create. On
DB2 / MySQL / PostgreSQL the same intent is one call: `CREATE OR REPLACE VIEW ...`."""),
        code("q(\"DROP VIEW empinfo\")\nq(\"CREATE VIEW empinfo AS SELECT emp_id, f_name, l_name, dep_id FROM employee WHERE dep_id <> 'D30'\")\nq(\"SELECT * FROM empinfo\")"),
        md("## 🧪 DROP the view"),
        code("q(\"DROP VIEW empinfo\")\nq(\"SELECT name, type FROM sqlite_master WHERE type = 'view'\")"),
        md("""## 📕 Dialect notes

- View replacement: SQLite = DROP + CREATE; `CREATE OR REPLACE VIEW` works on
  DB2, MySQL, PostgreSQL, Oracle.
- **Rule from the course**: views shouldn't hide `ORDER BY` — ordering belongs to the
  outer query; some engines ignore it inside a view anyway."""),
        md("""## 💡 Tips & tricks

- Views hide sensitive columns (a free security layer) and save complex joins for reuse.
- Read-only here: SQLite only supports **simple** updatable views (INSERT THROUGH
  view is limited) — treat views as read models.

## 🎯 Your turn

1. Create `emp_salaries` view with names + salaries (this one is internal-only).
2. Query it for department D11, then replace the view to exclude D11 too."""),
        code("""# 💡 Solution
q("CREATE VIEW emp_salaries AS SELECT f_name, l_name, salary, dep_id FROM employee")
q("SELECT * FROM emp_salaries WHERE dep_id = 'D11'")
q("DROP VIEW emp_salaries")
# SQLite has no CREATE OR REPLACE VIEW - the portable recipe is drop + create:
q("CREATE VIEW emp_salaries AS SELECT f_name, l_name, salary, dep_id FROM employee WHERE dep_id <> 'D11'")
q("SELECT * FROM emp_salaries")

# In engines that support it (DB2 / MySQL / PostgreSQL) the same intent is one line:
#   CREATE OR REPLACE VIEW emp_salaries AS SELECT ...""")
    ]

def nb28():
    return [
        _intro("28", "Stored Procedures", "7 — Advanced server", "28-stored-procedures.md",
            ["explain what a stored procedure is and why engines love them",
             "read the course's MySQL update_sal procedure",
             "emulate one with a Python function — SQLite's reality"]),
        md("""## 📗 What is a stored procedure?

A **named, saved procedure of SQL stored *in the database***. Called instead of
sending statements one by one. Benefits:

- ✅ Encapsulation — logic lives inside the db; applications just call it
- ✅ Performance — parsed/optimized once (and no per-statement round trips)
- ✅ Security — you can grant EXECUTE without raw-table permissions
- ✅ Reduced network traffic

**SQLite reality check:** SQLite has **no stored procedure language** — so the course's
MySQL procedure is studied as-is, and its behavior is emulated with a Python function
calling parameterized SQL (which is what nb22 trained you for)."""),
        md("""## 📕 The course's MySQL procedure (non-runnable here, learnable anywhere)

```sql
DELIMITER //
CREATE PROCEDURE update_sal (IN emp_num CHAR(6), IN rating INT)
BEGIN
    IF rating = 1 THEN
        UPDATE employees SET salary = salary * 1.10
        WHERE emp_num = emp_num;
    ELSE
        UPDATE employees SET salary = salary * 1.05
        WHERE emp_num = emp_num;
    END IF;
END //
DELIMITER ;
CALL update_sal('E1234', 1);   -- how the app invokes it
```"""),
        md("## 🧪 Build the same behavior in Python + SQLite"),
        code(SETUP_SQL + "\n"),
        code("""q("CREATE TABLE employees (emp_num TEXT PRIMARY KEY, name TEXT, salary REAL)")
q(\"\"\"
INSERT INTO employees VALUES
    ('E1234','Raul',100000), ('E2345','Rav',80000), ('E3456','Ana',60000)
\"\"\")
q("SELECT * FROM employees")"""),
        code("""def update_sal(conn, emp_num, rating):
    \"\"\"Emulates the stored procedure: +10% for rating 1, +5% otherwise.\"\"\"
    factor = 1.10 if rating == 1 else 1.05
    with conn:
        cur = conn.execute(
            "UPDATE employees SET salary = ROUND(salary * ?, 2) WHERE emp_num = ?",
            (factor, emp_num))
        return cur.rowcount

print(update_sal(conn, 'E1234', 1))   # like CALL update_sal('E1234', 1)
q("SELECT * FROM employees")"""),
        code("update_sal(conn, 'E2345', 1)\nupdate_sal(conn, 'E3456', 2)   # not rating 1 → only 5%\nq(\"SELECT emp_num, name, salary FROM employees ORDER BY salary DESC\")"),
        md("""## 💡 Tips & tricks

- Parameterize, never f-string: the procedure body above uses `?` placeholders exactly
  like a stored proc uses parameters.
- If you later meet DB2/Postgres (CREATE PROCEDURE / LANGUAGE SQL PL/pgSQL), the
  CALL semantics match this emulation.
- In analytics pipelines, a Python function + parameterized SQL is often *simpler* than
  a server-side proc — know both.

## 🎯 Your turn

1. Add a 3-rating rule of your own (rating 3 → −10%) to update_sal.
2. Build and call your own 'procedure' `hire_employee` that INSERTs a new employee."""),
        code("""# 💡 Solution
def update_sal2(conn, emp_num, rating):
    factor = {1: 1.10, 2: 1.05, 3: 0.90}[rating]
    with conn:
        conn.execute("UPDATE employees SET salary = ROUND(salary * ?, 2) WHERE emp_num = ?",
                     (factor, emp_num))
update_sal2(conn, 'E3456', 3)
q("SELECT * FROM employees WHERE emp_num = 'E3456'")

def hire_employee(conn, num, name, salary):
    with conn:
        conn.execute("INSERT INTO employees VALUES (?, ?, ?)", (num, name, salary))
hire_employee(conn, 'E9999', 'You', 72000)
q("SELECT * FROM employees WHERE emp_num = 'E9999'")"""),
    ]

def nb29():
    return [
        _intro("29", "ACID & Transactions", "7 — Advanced server", "29-acid-transactions.md",
            ["state what ACID stands for, property by property",
             "run a COMMIT path and a ROLLBACK path in sqlite",
             "see isolation in action: the money-transfer example"]),
        md("""## 📗 ACID

| Property | Meaning | Transfer example |
|---|---|---|
| **A**tomicity | all statements commit or none | send $200 A→B: both sides, or none |
| **C**onsistency | constraints hold after commit | money never appears from nowhere |
| **I**solation | concurrent transactions don't see each other's mid-states | your balance doesn't show partial deduct |
| **D**urability | committed data survives crash | confirmed transfer stays after power outage |"""),
        code(SETUP_SQL),
        md("## 🧪 The transfer story — setup"),
        code("""q("CREATE TABLE accounts (id TEXT PRIMARY KEY, owner TEXT, balance REAL)")
q("INSERT INTO accounts VALUES ('A','Alice',1000), ('B','Bob',300)")
conn.commit()                        # seed data committed, so the demos below
                                     # can open their own explicit transactions
                                     # (sqlite3 otherwise keeps an implicit txn open
                                     #  after writes, and BEGIN inside it fails)
q("SELECT * FROM accounts")"""),
        md("## 🧪 Path 1 — a clean transfer, ends in COMMIT"),
        code("""amount = 200
try:
    conn.execute("BEGIN")
    conn.execute("UPDATE accounts SET balance = balance - ? WHERE id = 'A'", (amount,))
    conn.execute("UPDATE accounts SET balance = balance + ? WHERE id = 'B'", (amount,))
    conn.execute("COMMIT")                      # atomicity: both or nothing
    print('✅ transfer committed')
except Exception as e:
    conn.execute("ROLLBACK")
    print('rolled back:', e)
q("SELECT * FROM accounts")"""),
        md("""## 🧪 Path 2 — a dirty transfer: rollback undoes everything

Alice has 800 left after the first transfer! Transferring 800 must fail *halfway* —
and rollback must erase the first UPDATE:"""),
        code("""amount = 800
try:
    conn.execute("BEGIN")
    conn.execute("UPDATE accounts SET balance = balance - ? WHERE id = 'A'", (amount,))
    q("SELECT id, balance FROM accounts WHERE id = 'A'")      # visible inside the txn!
    balance = conn.execute("SELECT balance FROM accounts WHERE id = 'A'").fetchone()[0]
    if balance < 300:                                          # keep a minimum balance
        raise ValueError(f'A would drop below minimum (balance={balance})')
    conn.execute("UPDATE accounts SET balance = balance + ? WHERE id = 'B'", (amount,))
    conn.execute("COMMIT")
except ValueError as e:
    conn.execute("ROLLBACK")
    print('❌ transaction rolled back:', e)
q("SELECT * FROM accounts")"""),
        md("""## 🧪 Isolation check — a second connection can't see the uncommitted work

We open a **file-based** DB so two connections (= two "sessions") can point at the
exact same database, and watch what each one sees mid-transaction:"""),
        code("""# Use a real file so both connections point at the same DB.
import os, tempfile
p = os.path.join(tempfile.mkdtemp(), 'bank.db')
c1 = sqlite3.connect(p, isolation_level=None)   # autocommit off, manual BEGIN
c2 = sqlite3.connect(p, isolation_level=None)
c1.execute("CREATE TABLE t (v INTEGER)")
c1.execute("INSERT INTO t VALUES (1)")
c1.execute("BEGIN")
c1.execute("INSERT INTO t VALUES (2)")
print('c1 sees:', c1.execute('SELECT * FROM t').fetchall())          # 1,2
print('c2 sees:', c2.execute('SELECT * FROM t').fetchall())          # only [1]!
c1.execute("COMMIT")
print('after commit, c2 sees:', c2.execute('SELECT * FROM t').fetchall())
db_path = p   # (kept for reference)"""),
        md("""## 💡 Tips & tricks

- Golden habits from the course: keep transactions **short**, commit at a
  *logical point*, always pair every error path with ROLLBACK.
- Python's `with connection:` is a one-line transaction — nb22 showed both spellings.
- Durability in SQLite: a `journal_mode=WAL` file db survives crashes mid-write.

## 🎯 Your turn

1. Transfer 100 from B to A twice in one transaction — commit, check balances add up.
2. Make a transaction fail *by constraint* (transfer more than A's balance into a
   `CHECK (balance >= 0)`-guarded table... try the CHECK!) and watch rollback fire."""),
        code("""# 💡 Solution
q("BEGIN")
conn.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 'B'")
conn.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 'A'")
conn.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 'B'")
conn.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 'A'")
conn.execute("COMMIT")
q("SELECT * FROM accounts")

c = sqlite3.connect(os.path.join(tempfile.mkdtemp(), 'guarded.db'), isolation_level=None)
c.execute("CREATE TABLE acct (id TEXT PRIMARY KEY, balance REAL CHECK (balance >= 0))")
c.execute("INSERT INTO acct VALUES ('X', 100)")
c.execute("BEGIN")
try:
    c.execute("UPDATE acct SET balance = -50 WHERE id = 'X'")
    print('constraint unexpectedly allowed it!')
except sqlite3.IntegrityError as e:
    print('constraint fired:', e)
c.execute("ROLLBACK")
print('after constraint rollback:', c.execute('SELECT * FROM acct').fetchall())"""),
    ]

def build():
    import builder
    names = {
        "21-python-sql-apis-overview": nb21,
        "22-database-api-connections": nb22,
        "23-sql-magic": nb23,
        "24-real-world-csv-loading": nb24,
        "25-metadata-catalogs": nb25,
        "26-eda-with-sql-and-pandas": nb26,
        "27-views": nb27,
        "28-stored-procedures": nb28,
        "29-acid-transactions": nb29,
    }
    return {name: builder.make_notebook(fn()) for name, fn in names.items()}