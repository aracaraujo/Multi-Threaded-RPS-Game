# Multi Threaded RPS Game


## Overview

This program is a simple RPS game. It was implemented using a client/server architecture. The server is threaded to be able to handle several connections and run multiple games at a time.

## Instructions

Start the server by running in a terminal window

```
python3 server.py
```

### Open two more terminal windows to run the client side or use two different machines for each client.

If running in the same machine open two more terminals and run the following

```
python3 client.py
```

If running in different machines do the following steps:

1. Make sure to be in the same network
2. Open the client.py file in your preferred IDE and change the server name in line 4 by the IP address of the device running the server.
3. Run the client.py file 
```
python3 clien.py
```

