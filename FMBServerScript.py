import socket
import struct
import sqlite3
import logging

# Setup logging
logging.basicConfig(filename='server.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Database setup
def setup_database():
    conn = sqlite3.connect('teltonika_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS gps_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        imei TEXT,
                        timestamp INTEGER,
                        latitude REAL,
                        longitude REAL,
                        speed REAL,
                        course REAL,
                        altitude REAL,
                        satellites INTEGER
                    )''')
    conn.commit()
    return conn

# Function to parse Teltonika Codec8 data
def parse_teltonika_data(data):
    try:
        if len(data) < 2:
            logging.error("Data is too short to contain valid IMEI information.")
            return []

        imei_length = data[0]  # First byte indicates IMEI length
        if len(data) < 1 + imei_length:
            logging.error("Data is too short to extract IMEI.")
            return []

        imei = data[1:1+imei_length].decode('utf-8', errors='ignore')  # Extract IMEI
        avl_data = data[1+imei_length:]  # Remaining AVL data
        
        if len(avl_data) < 10:
            logging.error("AVL data is too short, possible incomplete packet.")
            return []
        
        codec_id = avl_data[0]
        number_of_data = avl_data[1]
        parsed_data = []
        
        index = 2  # Start of AVL data array after codec_id and number_of_data
        for _ in range(number_of_data):
            if len(avl_data[index:]) < 24:
                logging.error("Not enough data for a full AVL record.")
                break
            
            timestamp = struct.unpack(">Q", avl_data[index:index+8])[0]
            priority = avl_data[index+8]
            longitude = struct.unpack(">i", avl_data[index+9:index+13])[0] / 10000000
            latitude = struct.unpack(">i", avl_data[index+13:index+17])[0] / 10000000
            altitude = struct.unpack(">h", avl_data[index+17:index+19])[0]
            angle = struct.unpack(">H", avl_data[index+19:index+21])[0]
            satellites = avl_data[index+21]
            speed = struct.unpack(">H", avl_data[index+22:index+24])[0]
            
            parsed_data.append({
                "imei": imei,
                "timestamp": timestamp,
                "latitude": latitude,
                "longitude": longitude,
                "altitude": altitude,
                "speed": speed,
                "course": angle,
                "satellites": satellites
            })
            index += 24  # Adjust index to next record
        return parsed_data
    except Exception as e:
        logging.error(f"Error parsing data: {e}")
        return []

# Function to save data into the database
def save_to_database(conn, data):
    cursor = conn.cursor()
    for record in data:
        cursor.execute('''INSERT INTO gps_data (imei, timestamp, latitude, longitude, speed, course, altitude, satellites)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                          (record['imei'], record['timestamp'], record['latitude'], record['longitude'], 
                           record['speed'], record['course'], record['altitude'], record['satellites']))
    conn.commit()

# TCP Server to receive data
def start_server(host='91.234.195.212', port=50120):
    conn = setup_database()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    logging.info(f"Server started on {host}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        logging.info(f"Connection from {addr}")
        
        try:
            data = client_socket.recv(1024)
            logging.info(f"Received data: {data.hex()}")
            
            parsed_data = parse_teltonika_data(data)
            save_to_database(conn, parsed_data)
            
            client_socket.send(struct.pack(">L", len(data)))
        except Exception as e:
            logging.error(f"Error handling client {addr}: {e}")
        finally:
            client_socket.close()

if __name__ == "__main__":
    start_server()
