import logging
import json
import sqlite3
import socket
from datetime import datetime

import select

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

PORT = 65432
HOST = "127.0.0.1"


def setup_database():
    conn = sqlite3.connect(
        "station_data.sqlite", timeout=10, isolation_level="DEFERRED"
    )
    cursor = conn.cursor()
    logger.info("Setting up stations database ...")
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS station_status (station_id INT PRIMARY KEY ,last_date TEXT, alarm1 INT,alarm2 INT);"""
    )
    if conn.total_changes > 0:
        logger.info("Creating new Station database")
        conn.commit()
    conn.close()
    logger.info("Station Database setup complete")


def parsing_data(data: str):
    if not data.strip():
        logger.debug("Handling empty data")
        return -1, -1, -1
    try:
        data = json.loads(data)
        logger.info(f"Processing received data-->\t{data}")
        station_id, alarm1, alarm2 = [int(data.get(key, -1)) for key in data]

    except (json.JSONDecodeError, ValueError, TypeError) as e:
        logger.error(f"Error handling data -->\t{e}")
        return -1, -1, -1

    return alarm1, alarm2, station_id


def process_client_data(data: str):
    alarm1, alarm2, station_id = parsing_data(data)
    last_data = datetime.now().strftime("%Y-%m-%d %H:%M")
    if station_id == -1 or alarm1 == -1 or alarm2 == -1:
        return

    with sqlite3.connect(
            "station_data.sqlite", timeout=10, isolation_level="DEFERRED"
    ) as conn:
        cursor = conn.cursor()
        logger.info(f"Inserting Updating station {station_id} in database")
        cursor.execute(
            """INSERT OR REPLACE INTO station_status (station_id,last_date,alarm1,alarm2)
        VALUES (?,?,?,?);""",
            (
                station_id,
                last_data,
                alarm1,
                alarm2,
            ),
        )
        if conn.total_changes > 0:
            logger.info("Changes detected,commiting to database")
            conn.commit()
        else:
            logger.info("No changes detected")
    logger.info("Database operation complete")


def server():
    setup_database()
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.bind((HOST, PORT))
    connection.listen(5)
    connection.setblocking(False)
    inputs = [connection]  # Sockets to monitor for incoming data
    outputs = []  # Sockets ready for writing (not used in this example)
    logger.info("is running and waiting for connections...")

    try:
        while True:
            readable, writable, exceptional = select.select(inputs, outputs, inputs)
            for s in readable:
                if s is connection:
                    logger.info("Handling data from a new client")
                    client_socket, addr = connection.accept()
                    logger.info(f"accepting new data from-->\t{addr}")
                    client_socket.setblocking(False)
                    inputs.append(client_socket)
                else:
                    try:
                        data = s.recv(1024).decode("utf-8")
                        process_client_data(data)
                    except socket.error:
                        inputs.remove(s)
                        s.close()
    except KeyboardInterrupt:
        logger.info("Shutting down Server .....")

    finally:
        connection.close()
        logger.info("shutting down connection complete ")


if __name__ == "__main__":
    server()
