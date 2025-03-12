import socket
import time
import argparse
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)
WAIT_TIME = 60


def read_status_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
                logger.info("Finished reading data from status.json")
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON -->\n  {e}")
                return None, None, None
            station_id, alarm1, alarm2 = [data.get(key) for key in data.keys()]
            if all(value is not None for value in [station_id, alarm1, alarm2]):
                logger.info(
                    f"Reading data succeeded-->\n Station ID: {station_id}, Alarm#1: {alarm1}, Alarm2: {alarm2}"
                )
                return station_id, alarm1, alarm2
            else:
                raise ValueError("Invalid Json Format: Missing keys in the file")
    except Exception as e:
        logger.error(f"Error reading status file -->\t {e}")
        return None, None, None


def client() -> None:
    parser = argparse.ArgumentParser(
        description="Client for sending station data to server."
    )
    parser.add_argument(
        "--wait_time",
        type=int,
        default=WAIT_TIME,
        help="Time in seconds between sending data",
    )
    parser.add_argument(
        "--status_file",
        type=str,
        default="status.json",
        help="Specify status file for the client",
    )
    args = parser.parse_args()

    wait_time = args.wait_time
    status_file = args.status_file
    server_address = ("127.0.0.1", 65432)
    try:
        while True:
            station_id, alarm1, alarm2 = read_status_file(status_file)
            if station_id is None:
                logger.error("Failed to read status file")
                time.sleep(wait_time)
                continue
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                    logger.info("Connecting to socket....")
                    client_socket.connect(server_address)
                    data = json.dumps(
                        {"station_id": station_id, "alarm1": alarm1, "alarm2": alarm2}
                    )
                    if data and data.strip():
                        client_socket.sendall(data.encode("utf-8"))
                        logger.info(f"Current Data Sent -->\t {data}")
            except Exception as e:
                logger.error(f"Cannot connect to socket-->{e}")

            time.sleep(wait_time)

    except KeyboardInterrupt:
        logger.info("Shutting down client .....")


if __name__ == "__main__":
    client()
