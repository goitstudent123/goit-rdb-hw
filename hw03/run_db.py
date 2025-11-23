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
CSV_DIR = "csv"   # adjust if needed

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
    print(f"Table/Description: {title}")
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


def print_query_result(conn: psycopg.Connection, sql: str, params: tuple | None = None, title: str | None = None) -> None:
    """Execute an arbitrary SQL query and pretty-print the result as a table."""
    with conn.cursor() as cur:
        cur.execute(sql, params or ())

        # If the statement does not return rows (e.g. INSERT/UPDATE/DDL)
        if cur.description is None:
            affected = cur.rowcount
            print()
            print("=" * 80)
            print("Query executed (no result set)")
            print("=" * 80)
            print(f"Rows affected: {affected}")
            return

        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]

    # Default title = first line of SQL if not provided explicitly
    if title is None:
        first_line = sql.strip().splitlines()[0]
        title = first_line if len(first_line) < 70 else first_line[:67] + "..."

    print_table(columns, rows, title=title)


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

def import_csv(conn: psycopg.Connection):
    COPY_COMMANDS = [
        # filename, COPY SQL (колонки в тому самому порядку, що й у CSV)
        ("categories.csv",
         "COPY categories (id, name, description) FROM STDIN WITH CSV HEADER"),
        ("customers.csv",
         "COPY customers (id, name, contact, address, city, postal_code, country) "
         "FROM STDIN WITH CSV HEADER"),
        ("employees.csv",
         "COPY employees (employee_id, last_name, first_name, birthdate, photo, notes) "
         "FROM STDIN WITH CSV HEADER"),
        ("shippers.csv",
         "COPY shippers (id, name, phone) FROM STDIN WITH CSV HEADER"),
        ("suppliers.csv",
         "COPY suppliers (id, name, contact, address, city, postal_code, country, phone) "
         "FROM STDIN WITH CSV HEADER"),
        ("products.csv",
         "COPY products (id, name, supplier_id, category_id, unit, price) "
         "FROM STDIN WITH CSV HEADER"),
        ("orders.csv",
         "COPY orders (id, customer_id, employee_id, date, shipper_id) "
         "FROM STDIN WITH CSV HEADER"),
        ("order_details.csv",
         "COPY order_details (id, order_id, product_id, quantity) "
         "FROM STDIN WITH CSV HEADER"),
    ]

    with conn.cursor() as cur:
        for filename, sql in COPY_COMMANDS:
            path = os.path.join(CSV_DIR, filename)
            print(f"Importing {path}...")

            with open(path, "r", encoding="utf-8") as f:
                # psycopg3 COPY API
                with cur.copy(sql) as copy:
                    for line in f:
                        copy.write(line)

    conn.commit()



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
        # import csvs from csv_dataset.zip
        run_sql_script_from_file(conn, "0_step_init.sql")
        import_csv(conn)
        run_sql_script_from_file(conn, "0_library_schema_init.sql")
        run_sql_script_from_file(conn, "0_library_schema_data.sql")

        queries = {
            "SET search_path TO public": "Switch to public",
            """
            SELECT
                od.id              AS order_detail_id,
                o.id               AS order_id,
                o.date             AS order_date,
                c.id               AS customer_id,
                c.name             AS customer_name,
                c.country          AS customer_country,
                p.id               AS product_id,
                p.name             AS product_name,
                p.price            AS product_price,
                cat.id             AS category_id,
                cat.name           AS category_name,
                e.employee_id      AS employee_id,
                e.first_name       AS employee_first_name,
                e.last_name        AS employee_last_name,
                sh.id              AS shipper_id,
                sh.name            AS shipper_name,
                sup.id             AS supplier_id,
                sup.name           AS supplier_name
            FROM order_details od
                INNER JOIN orders      o   ON od.order_id    = o.id
                INNER JOIN customers   c   ON o.customer_id  = c.id
                INNER JOIN products    p   ON od.product_id  = p.id
                INNER JOIN categories  cat ON p.category_id  = cat.id
                INNER JOIN employees   e   ON o.employee_id  = e.employee_id
                INNER JOIN shippers    sh  ON o.shipper_id   = sh.id
                INNER JOIN suppliers   sup ON p.supplier_id  = sup.id;
            """: """
            Напишіть запит за допомогою операторів FROM та INNER JOIN, що об’єднує всі таблиці даних, які ми завантажили з файлів: order_details, orders, customers, products, categories, employees, shippers, suppliers. 
            """,
            """
            SELECT COUNT(*) AS row_count
            FROM order_details od
                INNER JOIN orders      o   ON od.order_id    = o.id
                INNER JOIN customers   c   ON o.customer_id  = c.id
                INNER JOIN products    p   ON od.product_id  = p.id
                INNER JOIN categories  cat ON p.category_id  = cat.id
                INNER JOIN employees   e   ON o.employee_id  = e.employee_id
                INNER JOIN shippers    sh  ON o.shipper_id   = sh.id
                INNER JOIN suppliers   sup ON p.supplier_id  = sup.id;
            """: """
            Визначте, скільки рядків ви отримали (за допомогою оператора COUNT).
            """,
            """
            SELECT COUNT(*) AS row_count
            FROM order_details od
                INNER JOIN orders      o   ON od.order_id    = o.id
                INNER JOIN customers   c   ON o.customer_id  = c.id
                INNER JOIN products    p   ON od.product_id  = p.id
                INNER JOIN categories  cat ON p.category_id  = cat.id
                INNER JOIN employees   e   ON o.employee_id  = e.employee_id
                INNER JOIN shippers    sh  ON o.shipper_id   = sh.id
                LEFT JOIN suppliers    sup ON p.supplier_id  = sup.id;
            """: """
            Змініть декілька операторів INNER на LEFT чи RIGHT. Визначте, що відбувається з кількістю рядків. Чому? Напишіть відповідь у текстовому файлі.
            """,
            """
            SELECT
                od.id              AS order_detail_id,
                o.id               AS order_id,
                o.date             AS order_date,
                c.id               AS customer_id,
                c.name             AS customer_name,
                c.country          AS customer_country,
                p.id               AS product_id,
                p.name             AS product_name,
                p.price            AS product_price,
                cat.id             AS category_id,
                cat.name           AS category_name,
                e.employee_id      AS employee_id,
                e.first_name       AS employee_first_name,
                e.last_name        AS employee_last_name,
                sh.id              AS shipper_id,
                sh.name            AS shipper_name,
                sup.id             AS supplier_id,
                sup.name           AS supplier_name
            FROM order_details od
                INNER JOIN orders      o   ON od.order_id    = o.id
                INNER JOIN customers   c   ON o.customer_id  = c.id
                INNER JOIN products    p   ON od.product_id  = p.id
                INNER JOIN categories  cat ON p.category_id  = cat.id
                INNER JOIN employees   e   ON o.employee_id  = e.employee_id
                INNER JOIN shippers    sh  ON o.shipper_id   = sh.id
                INNER JOIN suppliers   sup ON p.supplier_id  = sup.id
            WHERE e.employee_id > 3
              AND e.employee_id <= 10;
            """: """
            На основі запита з пункта 3 виконайте наступне: оберіть тільки ті рядки, де employee_id > 3 та ≤ 10.
            """,
            """
                SELECT
                    cat.name       AS category_name,
                    od.quantity    AS quantity
                FROM order_details od
                    INNER JOIN orders      o   ON od.order_id    = o.id
                    INNER JOIN customers   c   ON o.customer_id  = c.id
                    INNER JOIN products    p   ON od.product_id  = p.id
                    INNER JOIN categories  cat ON p.category_id  = cat.id
                    INNER JOIN employees   e   ON o.employee_id  = e.employee_id
                    INNER JOIN shippers    sh  ON o.shipper_id   = sh.id
                    INNER JOIN suppliers   sup ON p.supplier_id  = sup.id
                WHERE e.employee_id > 3
                  AND e.employee_id <= 10
            """: """
            Згрупуйте за іменем категорії, порахуйте кількість рядків у групі, середню кількість товару (кількість товару знаходиться в order_details.quantity)
            """,
            """
                        WITH joined AS (
                SELECT
                    cat.name       AS category_name,
                    od.quantity    AS quantity
                FROM order_details od
                    INNER JOIN orders      o   ON od.order_id    = o.id
                    INNER JOIN customers   c   ON o.customer_id  = c.id
                    INNER JOIN products    p   ON od.product_id  = p.id
                    INNER JOIN categories  cat ON p.category_id  = cat.id
                    INNER JOIN employees   e   ON o.employee_id  = e.employee_id
                    INNER JOIN shippers    sh  ON o.shipper_id   = sh.id
                    INNER JOIN suppliers   sup ON p.supplier_id  = sup.id
                WHERE e.employee_id > 3
                  AND e.employee_id <= 10
            )
            SELECT
                category_name,
                COUNT(*)              AS row_count,
                AVG(quantity)         AS avg_quantity
            FROM joined
            GROUP BY category_name
            HAVING AVG(quantity) > 21
            """: """
            Відфільтруйте рядки, де середня кількість товару більша за 21.
            """,
            """
                        WITH joined AS (
                SELECT
                    cat.name       AS category_name,
                    od.quantity    AS quantity
                FROM order_details od
                    INNER JOIN orders      o   ON od.order_id    = o.id
                    INNER JOIN customers   c   ON o.customer_id  = c.id
                    INNER JOIN products    p   ON od.product_id  = p.id
                    INNER JOIN categories  cat ON p.category_id  = cat.id
                    INNER JOIN employees   e   ON o.employee_id  = e.employee_id
                    INNER JOIN shippers    sh  ON o.shipper_id   = sh.id
                    INNER JOIN suppliers   sup ON p.supplier_id  = sup.id
                WHERE e.employee_id > 3
                  AND e.employee_id <= 10
            )
            SELECT
                category_name,
                COUNT(*)              AS row_count,
                AVG(quantity)         AS avg_quantity
            FROM joined
            GROUP BY category_name
            HAVING AVG(quantity) > 21
            ORDER BY row_count DESC
            """: """
            Відсортуйте рядки за спаданням кількості рядків.
            """,
            """
            WITH joined AS (
                SELECT
                    cat.name       AS category_name,
                    od.quantity    AS quantity
                FROM order_details od
                    INNER JOIN orders      o   ON od.order_id    = o.id
                    INNER JOIN customers   c   ON o.customer_id  = c.id
                    INNER JOIN products    p   ON od.product_id  = p.id
                    INNER JOIN categories  cat ON p.category_id  = cat.id
                    INNER JOIN employees   e   ON o.employee_id  = e.employee_id
                    INNER JOIN shippers    sh  ON o.shipper_id   = sh.id
                    INNER JOIN suppliers   sup ON p.supplier_id  = sup.id
                WHERE e.employee_id > 3
                  AND e.employee_id <= 10
            )
            SELECT
                category_name,
                COUNT(*)              AS row_count,
                AVG(quantity)         AS avg_quantity
            FROM joined
            GROUP BY category_name
            HAVING AVG(quantity) > 21
            ORDER BY row_count DESC
            OFFSET 1
            LIMIT 4;
            """: """
            Виведіть на екран (оберіть) чотири рядки з пропущеним першим рядком.
            """,
        }
        for query, title in queries.items():
            print_query_result(conn, query, title=title)


if __name__ == "__main__":
    main()