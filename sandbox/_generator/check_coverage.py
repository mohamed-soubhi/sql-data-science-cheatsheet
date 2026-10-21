"""Coverage check: every lecture's key concepts must appear in its notebook."""
import io
import json
import pathlib

SB = pathlib.Path(__file__).resolve().parent.parent

KEYWORDS = {
    "00-START-HERE": ["launch", "module", "pandas"],
    "01-course-welcome-and-overview": ["roadmap", "Module 1", "SELECT"],
    "02-sql-databases-and-rdbms": ["CREATE TABLE", "INSERT INTO", "SELECT", "UPDATE", "DELETE", "RDBMS", "WHERE age > 30"],
    "03-types-of-sql-statements-ddl-vs-dml": ["CREATE", "ALTER", "TRUNCATE", "DROP", "INSERT", "SELECT", "DDL", "DML"],
    "04-database-concepts-relational-model": ["entity", "attribute", "primary key", "foreign key", "REFERENCES"],
    "05-create-table": ["CREATE TABLE", "PRIMARY KEY", "NOT NULL", "IntegrityError"],
    "06-alter-drop-and-truncate": ["ALTER TABLE", "ADD COLUMN", "DROP COLUMN", "DROP TABLE", "TRUNCATE", "DELETE FROM"],
    "07-insert-statement": ["INSERT INTO", "VALUES", "values for 3 columns"],
    "08-select-statement-where-clause": ["SELECT", "WHERE", "AND", "OR", "<>", ">=", "<="],
    "09-count-distinct-limit": ["COUNT", "DISTINCT", "LIMIT"],
    "10-update-and-delete": ["UPDATE", "DELETE FROM", "WHERE", "rollback"],
    "11-like-between-in": ["LIKE", "BETWEEN", "IN (", "UPPER", "NOT IN"],
    "12-order-by": ["ORDER BY", "DESC", "ASC", "LIMIT", "ORDER BY 2"],
    "13-group-by-having-as": ["GROUP BY", "HAVING", "AS", "DISTINCT", "COUNT"],
    "14-builtin-sql-functions": ["SUM", "MIN", "MAX", "AVG", "ROUND", "LENGTH", "UPPER", "LOWER"],
    "15-date-and-time-functions": ["strftime", "DATE(", "julianday", "date('now')"],
    "16-sub-queries": ["(SELECT AVG", "(SELECT MAX", "FROM (SELECT", "misuse of aggregate" ],
    "17-working-with-multiple-tables": ["IN (SELECT", "FROM emp e", "Cartesian", "loc_id"],
    "18-join-overview": ["JOIN loan", "JOIN copy", "JOIN book", "borrower_id = l.borrower_id"],
    "19-inner-join": ["INNER JOIN", "ON b.borrower_id", "fan-out", "IS NULL"],
    "20-left-right-full-outer-join": ["LEFT OUTER JOIN", "RIGHT OUTER JOIN", "FULL OUTER JOIN", "COALESCE", "UNION"],
    "21-python-sql-apis-overview": ["connect(", "cursor", "execute", "close", "sqlite3"],
    "22-database-api-connections": ["fetchall", "fetchone", "executemany", "commit", "rollback", "close"],
    "23-sql-magic": ["load_ext", "sql", "magic", "pwd", "DB-API"],
    "24-real-world-csv-loading": ["read_csv", "to_sql", "read_sql", "backtick", "LIMIT"],
    "25-metadata-catalogs": ["sqlite_master", "PRAGMA table_info", "information_schema" if False else "catalog"],
    "26-eda-with-sql-and-pandas": ["describe()", "idxmax", "swarmplot", "jointplot", "boxplot"],
    "27-views": ["CREATE VIEW", "DROP VIEW", "re-compute"],
    "28-stored-procedures": ["PROCEDURE", "CALL", "update_sal", "1.10", "1.05"],
    "29-acid-transactions": ["BEGIN", "COMMIT", "ROLLBACK", "ACID", "Atomicity", "Isolation", "Durability"],
}

def sources(nb):
    for cell in nb["cells"]:
        src = cell["source"] if isinstance(cell["source"], str) else "".join(cell["source"])
        yield cell["cell_type"], src
        if cell["cell_type"] == "code":
            for out in cell.get("outputs", []):
                if "text" in out:
                    t = out["text"] if isinstance(out["text"], str) else "".join(out["text"])
                    yield "output", t
if __name__ == "__main__":
    bad = 0
    total_kw = 0
    for p in sorted(SB.glob("*.ipynb")):
        base = p.stem.replace(".ipynb", "")
        kws = KEYWORDS.get(base)
        if kws is None:
            continue
        nb = json.load(io.open(p, encoding="utf-8"))
        text = "\n".join(s for _, s in sources(nb)).lower()
        missing = [k for k in kws if k.lower() not in text]
        got = len(kws) - len(missing)
        total_kw += len(kws)
        status = "PASS" if not missing else "MISS " + " | ".join(missing)
        if missing:
            bad += 1
        print(f'{status:<6} {base}: {got}/{len(kws)} keywords')
    print(f'\ncoverage: {total_kw - bad if not bad else "SEE ABOVE"} - {bad} notebooks with gaps')