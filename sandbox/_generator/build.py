"""Build and execute all sandbox notebooks.

Usage (from sandbox/_generator):
    python build.py            # write + execute all notebooks in place
    python build.py --write-only
"""
import io
import os
import pathlib
import sys
import time
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import builder
import part1
import part2
import part3

SANDBOX = pathlib.Path(__file__).resolve().parent.parent
GENERATED = SANDBOX / "_generator"

def collect():
    builds = {}
    for mod, names in [
        (part1, ["00-START-HERE", "01-course-welcome-and-overview",
                 "02-sql-databases-and-rdbms", "03-types-of-sql-statements-ddl-vs-dml",
                 "04-database-concepts-relational-model", "05-create-table",
                 "06-alter-drop-and-truncate", "07-insert-statement",
                 "08-select-statement-where-clause", "09-count-distinct-limit",
                 "10-update-and-delete"]),
        (part2, ["11-like-between-in", "12-order-by", "13-group-by-having-as",
                 "14-builtin-sql-functions", "15-date-and-time-functions",
                 "16-sub-queries", "17-working-with-multiple-tables",
                 "18-join-overview", "19-inner-join", "20-left-right-full-outer-join"]),
        (part3, ["21-python-sql-apis-overview", "22-database-api-connections",
                 "23-sql-magic", "24-real-world-csv-loading", "25-metadata-catalogs",
                 "26-eda-with-sql-and-pandas", "27-views", "28-stored-procedures",
                 "29-acid-transactions"]),
    ]:
        for name in names:
            builds[name] = getattr(mod, "build")()[name]
    print(f'{len(builds)} notebooks authored')
    return builds

def write(builds):
    paths = builder.write_all(builds, SANDBOX)
    print(f'wrote {len(paths)} .ipynb files under {SANDBOX}')
    return paths

def execute(paths):
    """Headless execution with nbclient; rewrites files with outputs embedded."""
    from nbclient import NotebookClient
    from nbclient.exceptions import CellTimeoutError, CellExecutionError
    failed, ok = [], []
    for p in paths:
        import nbformat
        nb = nbformat.read(str(p), as_version=4)
        nb.metadata.setdefault("kernelspec", dict(builder._kernel))
        t0 = time.time()
        try:
            NotebookClient(nb, timeout=180, kernel_name='python3').execute()
            nbformat.write(nb, str(p))
            dt = time.time() - t0
            ok.append((p.name, dt))
            print(f'  OK   {p.name:<42} {dt:5.1f}s')
        except (CellTimeoutError, CellExecutionError) as e:
            failed.append(p.name)
            print(f'  FAIL {p.name:<42} {e}')
            buf = io.StringIO()
            traceback.print_exc(file=buf)
            print(buf.getvalue()[:4000])
    print(f'\n{len(ok)} executed clean, {len(failed)} failed')
    if failed:
        print('failed notebooks:', *failed, sep='\n  - ')
    return failed

def main():
    write_only = "--write-only" in sys.argv
    builds = collect()
    paths = write(builds)
    if not write_only:
        bad = execute(paths)
        sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()