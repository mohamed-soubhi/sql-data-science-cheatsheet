"""Notebook builder for the SQL study sandbox.

Provides tiny helpers so each lecture's content is a list of
(markdown | code) cells; produces nbformat v4 notebooks.
"""
import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

_kernel = {
    "name": "python3",
    "display_name": "Python 3 (ipykernel)",
    "language": "python",
}

def md(text):
    return new_markdown_cell(text)

def code(text):
    return new_code_cell(text)

def make_notebook(intro_cells):
    """intro_cells: list of markdown/code cells → notebook object."""
    return new_notebook(cells=list(intro_cells), metadata={
        "kernelspec": dict(_kernel, codemirror_mode={"name": "sql", "version": 2},
                           language_info={"name": "python"}),
        "language_info": {"name": "python", "version": "3.12"},
    })

# The standard setup + query-render helper used by every SQL notebook.
SETUP_SQL = """\
import sqlite3
import textwrap

conn = sqlite3.connect(':memory:')  # throw-away in-memory database
conn.execute("PRAGMA foreign_keys = ON")

def q(sql):
    \"\"\"Run a query, print formatted SQL, and display the result set as a table.\"\"\"
    clean_sql = textwrap.dedent(sql).strip()

    # 1. Print formatted SQL query
    print("\\n" + "=" * 60)
    print("QUERY:")
    print(textwrap.indent(clean_sql, "  "))
    print("-" * 60)

    cur = conn.execute(sql)
    rows = cur.fetchall()

    if cur.description:  # SELECT / statement returning rows
        headers = [d[0] for d in cur.description]
        str_rows = [[("" if v is None else str(v)) for v in r] for r in rows]

        # Calculate dynamic column widths for clean alignment
        widths = [
            max(len(h), *(len(r[i]) for r in str_rows), 1)
            for i, h in enumerate(headers)
        ] if str_rows else [len(h) for h in headers]

        header_line = " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
        sep_line = "-+-".join("-" * widths[i] for i in range(len(headers)))

        print(header_line)
        print(sep_line)
        for r in str_rows:
            print(" | ".join(val.ljust(widths[i]) for i, val in enumerate(r)))
        if not str_rows:
            print("(0 rows returned)")
    else:  # DDL / DML (CREATE, INSERT, UPDATE, DELETE)
        affected = cur.rowcount
        print(f"Done (rows affected: {affected})" if affected != -1 else "Done.")

    print("=" * 60)

print('Connection ready:', conn)"""

def try_sql_demo(body_sql, why):
    """A code cell that expects a failure and prints the db's error message."""
    return code(
        f'# Some course-syntax errors are lessons themselves — run and read the error.\n'
        f'import sqlite3\n'
        f'try:\n'
        + ''.join(f'    {line}\n' for line in body_sql.strip().split('\n'))
        + f'except sqlite3.Error as e:\n'
        + f'    print(repr(e))   # {why}'
    )

def write_all(builds, out_dir):
    """builds: dict filename -> notebook object. Writes .ipynb files."""
    import os, pathlib
    path = pathlib.Path(out_dir)
    path.mkdir(parents=True, exist_ok=True)
    written = []
    for name, nb in builds.items():
        p = path / f"{name}.ipynb"
        nbf.write(nb, str(p))
        written.append(p)
    return written