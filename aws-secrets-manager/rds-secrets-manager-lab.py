import json
import os
import time
import uuid
import logging

import boto3
import pymysql

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ---- Config ----
SECRET_NAME = os.getenv("SECRET_NAME", "prod/sampledb")
DB_NAME     = "sampledb"      # your DB name
TABLE_NAME  = "demo_items"    # demo table we create/use
INSERT_COL  = "item"          # text column we insert into

secrets = boto3.client("secretsmanager")

def get_db_params():
    resp = secrets.get_secret_value(SecretId=SECRET_NAME)
    secret_str = resp.get("SecretString") or resp.get("SecretBinary", b"").decode("utf-8")
    data = json.loads(secret_str)

    host = data.get("host")
    port = int(data.get("port", 3306))
    user = data.get("username") or data.get("user")
    password = data.get("password")

    if not all([host, user, password, DB_NAME]):
        raise ValueError("Secret must include host, username, password; DB_NAME is fixed in code.")

    return {"host": host, "port": port, "user": user, "password": password, "db": DB_NAME}

def connect_mysql(params):
    return pymysql.connect(
        host=params["host"],
        user=params["user"],
        password=params["password"],
        database=params["db"],
        port=params["port"],
        connect_timeout=5,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
        read_timeout=10,
        write_timeout=10,
    )

def ensure_demo_table(conn):
    with conn.cursor() as cur:
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS `{DB_NAME}`.`{TABLE_NAME}` (
                id INT AUTO_INCREMENT PRIMARY KEY,
                {INSERT_COL} VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
    conn.commit()

def insert_row(conn, value):
    with conn.cursor() as cur:
        cur.execute(
            f"INSERT INTO `{DB_NAME}`.`{TABLE_NAME}` (`{INSERT_COL}`) VALUES (%s);",
            (value,)
        )
        new_id = cur.lastrowid
    conn.commit()
    return new_id

def fetch_rows(conn, limit=50):
    with conn.cursor() as cur:
        cur.execute(
            f"SELECT id, `{INSERT_COL}` AS item, created_at "
            f"FROM `{DB_NAME}`.`{TABLE_NAME}` "
            f"ORDER BY id DESC LIMIT %s;",
            (limit,)
        )
        return cur.fetchall()

def lambda_handler(event, context):
    try:
        params = get_db_params()
        conn = connect_mysql(params)
        try:
            # 1) ensure table exists
            ensure_demo_table(conn)

            # 2) insert one row (or take from event)
            value = (event.get("item") if isinstance(event, dict) else None) \
                    or f"demo-{uuid.uuid4().hex[:8]}-{int(time.time())}"
            new_id = insert_row(conn, value)

            # 3) read rows
            limit = int(event.get("limit", 50)) if isinstance(event, dict) else 50
            rows = fetch_rows(conn, limit=limit)
        finally:
            conn.close()

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "db": DB_NAME,
                "table": TABLE_NAME,
                "inserted_id": new_id,
                "inserted_value": value,
                "rows": rows
            }, default=str)
        }

    except Exception as e:
        logger.exception("Error in handler")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
