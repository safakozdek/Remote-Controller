
# To Use
You need:
- Two computers(client & server) that are connected to the same local area network.
- Both computers should support linux OS.

# Usage
1. Run server.py on your remote computer.
   
``` 
# Run server
$ python3 server.py
```
2. Run client.py on your own computer.
   
``` 
# Run client
$ python3 client.py
```
3. Choose a name as client

4. After the handshake process(~10 secs), choose a command from list
 - Show my profile 
 - Send a terminal command 
 - Quit
 
 5. After choosing "Send a terminal command", type in your command to execute.
 
 # Notes
 
 - Remove commands are forbidden.
 - User needs to wait 5 seconds before sending another command.
 - Symetric encryption wrt RSSI value of client in both client and server side.
 - Filter mechanism according to RSSI value of client in the server side.
