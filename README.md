# Water Station Monitoring System

This project consists of a **server** and multiple **clients** that communicate using TCP sockets to monitor the status of water stations.

## **Project Structure**
- `server.py`: Runs the server to receive client data and store it in an SQLite database.
- `client.py`: Simulates a water station sending data to the server.
- `status.json`: Stores the station's ID and alarm states.
- `data.sqlite`: SQLite database file created and managed by `server.py`.

## **How to Run the Server**
1. Ensure all dependencies are installed (Python 3.7+ required).
2. Open a terminal and run:
   ```sh
   python server.py
   ```
3. The server will start listening for client connections.

## **How to Run Multiple Clients**
Each client instance requires a separate `status.json` file. You can run multiple clients by specifying different status files.

1. Create separate JSON files for each client:
   ```sh
   cp status.json client1.json
   cp status.json client2.json
   ```
2. Run multiple clients in separate terminal windows or background processes:
   ```sh
   python client.py --status_file client1.json
   python client.py --status_file client2.json
   ```
3. Each client will read from its respective JSON file and send data to the server at regular intervals.

## **Stopping the Server and Clients**
- To stop the **server**, press `CTRL+C` in the terminal.
- To stop the **clients**, close their respective terminal windows or use `CTRL+C`.

## **Troubleshooting**
- If the database is locked, ensure no other processes are holding the SQLite file.
- If a client is not sending data, verify the `status.json` format and restart the client.

## **Future Improvements**
- Implement authentication for clients.
- Add a web dashboard for real-time monitoring.
- Optimize database writes for better performance.

Enjoy working with the Water Station Monitoring System!
