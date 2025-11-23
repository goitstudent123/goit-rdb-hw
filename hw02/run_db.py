import os
import time
from contextlib import contextmanager

import docker
import psycopg
from psycopg.rows import dict_row

POSTGRES_IMAGE = "postgres:16-alpine"
DB_NAME = "testdb"
DB_USER = "testuser"
DB_PASSWORD = "secret"


def start_postgres_container():
    """Start a Postgres container with a random mapped host port."""
    client = docker.from_env()

    print("Pulling Postgres image if needed...")
    client.images.pull(POSTGRES_IMAGE)

    print("Starting Postgres container...")
    container = client.containers.run(
        POSTGRES_IMAGE,
        detach=True,
        remove=False,
        environment={
            "POSTGRES_DB": DB_NAME,
            "POSTGRES_USER": DB_USER,
            "POSTGRES_PASSWORD": DB_PASSWORD,
        },
        ports={"5432/tcp": None},
    )

    container.reload()
    ports = container.attrs["NetworkSettings"]["Ports"]
    mapped = ports.get("5432/tcp")
    if not mapped:
        raise RuntimeError("Failed to get mapped port for Postgres.")
    host_port = int(mapped[0]["HostPort"])

    print(f"Postgres container started on localhost:{host_port}")
    return container, host_port


def wait_for_postgres(port: int, timeout_seconds: int = 30) -> psycopg.Connection:
    """Wait until Postgres is ready to accept connections."""
    start = time.time()
    last_error = None

    while time.time() - start < timeout_seconds:
        try:
            conn = psycopg.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host="127.0.0.1",
                port=port,
                autocommit=True,
            )
            print("Postgres is ready.")
            return conn
        except Exception as exc:
            last_error = exc
            time.sleep(0.5)

    raise TimeoutError(f"Postgres did not become ready: {last_error}")


def run_sql_script_from_file(conn: psycopg.Connection, path_str: str) -> None:
    """Run all statements from a .sql file."""
    path = os.path.join(os.path.dirname(__file__), path_str)
    print(f"Running init script: {path_str}")
    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()
    run_sql_script(conn, sql)


def run_sql_script(conn: psycopg.Connection, sql: str) -> None:
    """Run a multi-statement SQL script."""
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    with conn.cursor() as cur:
        for stmt in statements:
            cur.execute(stmt)


def fetch_user_tables(conn: psycopg.Connection) -> list[str]:
    """Return a list of user tables in the public schema."""
    query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_type = 'BASE TABLE'
            ORDER BY table_name; \
            """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query)
        rows = cur.fetchall()
    return [row["table_name"] for row in rows]


def fetch_table_data(conn: psycopg.Connection, table_name: str) -> tuple[list[str], list[tuple]]:
    """Fetch all rows from a table and return (columns, rows)."""
    with conn.cursor() as cur:
        cur.execute(f'SELECT * FROM "{table_name}"')
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
    return columns, rows


def print_table(columns: list[str], rows: list[tuple], title: str) -> None:
    """Pretty print table data to console."""
    print()
    print("=" * 80)
    print(f"Table: {title}")
    print("=" * 80)

    if not rows:
        print("(no rows)")
        return

    col_widths = []
    for i, col in enumerate(columns):
        max_len = len(col)
        for row in rows:
            value = row[i]
            value_str = "" if value is None else str(value)
            max_len = max(max_len, len(value_str))
        col_widths.append(max_len)

    def format_row(values):
        cells = []
        for i, val in enumerate(values):
            value_str = "" if val is None else str(val)
            cells.append(value_str.ljust(col_widths[i]))
        return "| " + " | ".join(cells) + " |"

    header = format_row(columns)
    separator = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"

    print(separator)
    print(header)
    print(separator)
    for row in rows:
        print(format_row(row))
    print(separator)


def print_all_user_tables(conn: psycopg.Connection) -> None:
    """Query all user tables and print their contents."""
    tables = fetch_user_tables(conn)
    if not tables:
        print("No user tables found in 'public' schema.")
        return

    print("User tables in 'public' schema:")
    for name in tables:
        print(f" - {name}")

    for name in tables:
        columns, rows = fetch_table_data(conn, name)
        print_table(columns, rows, title=name)

    input("Press Enter to continue...")


def teardown_container(container) -> None:
    """Stop and remove Postgres container."""
    print("Stopping Postgres container...")
    try:
        container.stop(timeout=10)
    except Exception as exc:
        print(f"Error while stopping container: {exc}")

    print("Removing Postgres container...")
    try:
        container.remove(v=True, force=True)
    except Exception as exc:
        print(f"Error while removing container: {exc}")
    print("Container torn down.")


@contextmanager
def postgres_container():
    """Context manager: start Postgres, yield (conn, container), then tear down."""
    container = None
    conn = None
    try:
        container, port = start_postgres_container()
        conn = wait_for_postgres(port)
        yield conn, container
    finally:
        if conn is not None:
            conn.close()
        if container is not None:
            teardown_container(container)


def main():
    with postgres_container() as (conn, _container):
        scripts = [
            "0_step_init.sql",
            "1_step_to_1nf.sql",
            "2_step_to_2nf.sql",
            "3_step_to_3nf.sql",
            "4_step_to_final.sql"
        ]

        for script in scripts:
            run_sql_script_from_file(conn, script)
            print_all_user_tables(conn)


if __name__ == "__main__":
    main()
