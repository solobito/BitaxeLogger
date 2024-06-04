# Save the Bitaxe WebSocket and HTTPS logs in a file

**Requirements:**

1. Create a virtual environment:
    ```bash
    python3 -m venv .venv
    ```
2. Activate the virtual environment:
    ```bash
    source .venv/bin/activate
    ```
3. Install the dependencies:
    ```bash
    python3 -m pip install -r requirements.txt
    ```
4. Run the script using the IP address of your Bitaxe:
    ```bash
    python3 mywebsocket.py -ip 192.168.1.233
    ```
5. If you do not need WebSocket logs, run the script as follows:
    ```bash
    python3 mywebsocket.py -ip 192.168.1.233 -nowebsocket
    ```
6. The logs will be saved in the `db` folder.
