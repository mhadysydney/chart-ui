import socket
import struct
import sqlite3
import logging
from datetime import datetime

# Configuration
HOST = '91.234.195.212'  # Listen on all interfaces
PORT = 50120       # Port to listen on
LOG_FILE = 'server_v2.log'
DB_FILE = 'teltonika_data_v2.db'

# Set up logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Function to initialize the SQLite database
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gps_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            imei TEXT,
            timestamp INTEGER,
            priority INTEGER,
            longitude REAL,
            latitude REAL,
            altitude INTEGER,
            angle INTEGER,
            satellites INTEGER,
            speed INTEGER,
            io_count INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# Function to insert data into the SQLite database
def insert_gps_data(imei, timestamp, priority, longitude, latitude, altitude, angle, satellites, speed, io_count):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO gps_data (
            imei, timestamp, priority, longitude, latitude, altitude, angle, satellites, speed, io_count
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (imei, timestamp, priority, longitude, latitude, altitude, angle, satellites, speed, io_count))
    conn.commit()
    conn.close()

# Function to parse IMEI (device identifier)
def parse_imei(data):
    imei_length = int.from_bytes(data[:2], byteorder='big')
    imei = data[2:2 + imei_length].decode('utf-8')
    return imei

# Function to parse AVL data (GPS and other information)
def parse_avl_data(data, imei):
    # AVL data structure:
    # 1 byte - Codec ID
    # 1 byte - Number of data records
    # N bytes - Data records
    # 4 bytes - CRC-16 checksum

    codec_id = data[0]
    num_records = data[1]

    logging.info(f"Codec ID: {codec_id}")
    logging.info(f"Number of records: {num_records}")

    # Parse each data record
    offset = 2
    for _ in range(num_records):
        # Parse timestamp (8 bytes)
        timestamp = int.from_bytes(data[offset:offset + 8], byteorder='big')
        offset += 8

        # Parse priority (1 byte)
        priority = data[offset]
        offset += 1

        # Parse GPS data
        longitude = int.from_bytes(data[offset:offset + 4], byteorder='big') / 10000000
        latitude = int.from_bytes(data[offset + 4:offset + 8], byteorder='big') / 10000000
        altitude = int.from_bytes(data[offset + 8:offset + 10], byteorder='big')
        angle = int.from_bytes(data[offset + 10:offset + 12], byteorder='big')
        satellites = data[offset + 12]
        speed = int.from_bytes(data[offset + 13:offset + 15], byteorder='big')
        offset += 15

        # Parse IO elements (optional)
        io_count = data[offset]
        offset += 1

        # Insert data into the database
        insert_gps_data(imei, timestamp, priority, longitude, latitude, altitude, angle, satellites, speed, io_count)

        logging.info(f"IMEI: {imei}, Timestamp: {timestamp}, Priority: {priority}")
        logging.info(f"Longitude: {longitude}, Latitude: {latitude}")
        logging.info(f"Altitude: {altitude}, Angle: {angle}")
        logging.info(f"Satellites: {satellites}, Speed: {speed}")
        logging.info(f"IO Count: {io_count}")

    # Parse CRC-16 checksum (4 bytes)
    crc = int.from_bytes(data[offset:offset + 4], byteorder='big')
    logging.info(f"CRC-16: {crc}")

# Function to handle client connections
def handle_client(conn, addr):
    logging.info(f"Connected by {addr}")

    # Step 1: Receive IMEI
    imei_data = conn.recv(1024)
    imei = parse_imei(imei_data)
    logging.info(f"Device IMEI: {imei}")

    # Step 2: Send acknowledgment (1 byte: 0x01)
    conn.send(bytes([0x01]))

    # Step 3: Receive AVL data
    avl_data = conn.recv(4096)
    logging.info(f"Received AVL data: {avl_data.hex()}")
    parse_avl_data(avl_data, imei)

    # Step 4: Send acknowledgment (4 bytes: number of records)
    num_records = avl_data[1]
    conn.send(struct.pack('>I', num_records))

    conn.close()
    logging.info(f"Connection closed for {addr}")

# Main server function
def start_server():
    # Initialize the database
    init_db()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        logging.info(f"Server listening on {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            handle_client(conn, addr)

if __name__ == "__main__":
    start_server()
