import sys
from socket import *
import threading
import multiprocessing as mp
from _thread import *
import queue
import random
import time

def game(player1,player2):
    '''Returns who won the round according to RPS rules.'''

    if player1 == 'Q':
        return '1Q'
    if player2 == 'Q':
        return '2Q'
    if player1 == player2:
        return 'T'
    if (player1 == 'R' and player2 == 'S') or (player1 == 'S' and player2 == 'P') or (player1 == 'P' and player2 == 'R'):
        return '1W'
    if (player2 == 'R' and player1 == 'S') or (player2 == 'S' and player1 == 'P') or (player2 == 'P' and player1 == 'R'):
        return '2W'

def rps_game(id, connection_socket1, connection_socket2, thread_queue):
    '''This function runs the RPS game between the clients given in the parameters'''

    try:
        # Setting up variables.
        inputs = ['R','P','S','Q']
        score = {'1': 0, '2': 0}

        while True:
            playerOneChecker = False
            playerTwoChecker = False

            while not playerOneChecker:
                # Getting user 1 move.
                playerOneMove = connection_socket1.recv(1024).decode('UTF-8')

                if playerOneMove in inputs:
                    playerOneChecker = True

            while not playerTwoChecker:
                # Getting user 2 move.
                playerTwoMove = connection_socket2.recv(1024).decode('UTF-8')
                
                if playerTwoMove in inputs:
                    playerTwoChecker = True

            # Running the game function to see who won the round.
            gameResult = game(playerOneMove,playerTwoMove)   

            # Checking the results and then send the results back to the users.
            if gameResult == '1Q':
                score['2'] += 1
                connection_socket1.send('Q'.encode('UTF-8')) # Result
                connection_socket1.send(str(score['1']).encode('UTF-8'))
                connection_socket1.send(str(score['2']).encode('UTF-8'))
                connection_socket2.send('Q'.encode('UTF-8'))
                connection_socket2.send(str(score['2']).encode('UTF-8'))
                connection_socket2.send(str(score['1']).encode('UTF-8'))
                break
            elif gameResult == '2Q':
                score['1'] += 1
                connection_socket1.send('Q'.encode('UTF-8')) # Result
                connection_socket1.send(str(score['1']).encode('UTF-8'))
                connection_socket1.send(str(score['2']).encode('UTF-8'))
                connection_socket2.send('Q'.encode('UTF-8'))
                connection_socket2.send(str(score['2']).encode('UTF-8'))
                connection_socket2.send(str(score['1']).encode('UTF-8'))
                break
            elif gameResult == 'T':
                connection_socket1.send('T'.encode('UTF-8')) # Result
                connection_socket1.send(str(score['1']).encode('UTF-8'))
                connection_socket1.send(str(score['2']).encode('UTF-8'))
                connection_socket2.send('T'.encode('UTF-8'))
                connection_socket2.send(str(score['2']).encode('UTF-8'))
                connection_socket2.send(str(score['1']).encode('UTF-8'))
            elif gameResult == '1W':
                score['1'] += 1
                connection_socket1.send('W'.encode('ascii')) # Result
                connection_socket1.send(str(score['1']).encode('UTF-8'))
                connection_socket1.send(str(score['2']).encode('UTF-8'))
                connection_socket2.send('L'.encode('UTF-8'))
                connection_socket2.send(str(score['2']).encode('UTF-8'))
                connection_socket2.send(str(score['1']).encode('UTF-8'))
            elif gameResult == '2W':
                score['2'] += 1
                connection_socket1.send('L'.encode('UTF-8')) # Result
                connection_socket1.send(str(score['1']).encode('UTF-8'))
                connection_socket1.send(str(score['2']).encode('UTF-8'))
                connection_socket2.send('W'.encode('UTF-8'))
                connection_socket2.send(str(score['2']).encode('UTF-8'))
                connection_socket2.send(str(score['1']).encode('UTF-8'))

            if score['1'] == 9 or score['2'] == 9:
                break

        # Sending the game id to the queue so the manager can join the thread.
        thread_queue.put(id)

    # Handling exceptions to make sure that the threads will be join correctly.
    except BrokenPipeError:
        thread_queue.put(id)
    except ConnectionResetError:
        thread_queue.put(id)

def manager(connection_queue):
    '''This function will manage all the different games that are running at the same time.'''

    # Creating the threads queue.
    thread_queue = queue.Queue()
    thread_list = {}
    while True:

        # Checking the queue size and when has enough players it will start a game.
        if connection_queue.qsize() >= 2:
            
            # Getting two players from the queue.
            connection_socket1 = connection_queue.get()
            connection_socket2 = connection_queue.get()

            # Receving the players name.
            player1 = connection_socket1.recv(1024).decode('UTF-8')
            player2 = connection_socket2.recv(1024).decode('UTF-8')

            # Checking if any of the players quit the game.
            if player1 == 'Q':
                connection_socket2.send('Q'.encode('UTF-8'))
            elif player2 == 'Q':
                connection_socket1.send('Q'.encode('UTF-8'))
            else:
                connection_socket1.send(player2.encode('UTF-8'))
                connection_socket2.send(player1.encode('UTF-8'))

                # Generates a game id.
                id = random.randint(0,100)
                print(f'Game between {player1} and {player2} starting...')
                print(f'Game ID is: {id}')

                # Start a thread for that game.
                thread = threading.Thread(target=rps_game, args=(id, connection_socket1,connection_socket2,thread_queue))
                thread.start()
                # Add the thread and ID to a dictionary.
                thread_list[id] = thread
        
        try:
            # Checking the delete queue. If an ID was sent it will join the thread 
            # and delete the thread from the dictionary.
            id_to_delete = thread_queue.get()
            print(f'Game with ID: {id_to_delete} is finished.')
            thread_list[id_to_delete].join()
            del thread_list[id_to_delete]
        except:
            ...

# Setting up server socket.
DEFAULT_VALUE = 6789
serverPort = int(sys.argv[1]) if len(sys.argv) == 2 else DEFAULT_VALUE

server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(('', serverPort))
server_socket.listen(1)
connection_queue = queue.Queue()
print('The Server is ready to receive')

try:
    while 1:
        # Starting manage thread.
        manager_thread = threading.Thread(target=manager,args=(connection_queue,))
        manager_thread.start()
        # First player conecting.
        connection_socket1, addr1 = server_socket.accept()
        print(f'Connected to player 1: {addr1}')
        # Second player conecting.
        connection_socket2, addr2 = server_socket.accept()
        print(f'Connected to player 2: {addr2}')
        
        # Adding the connections to the queue.
        connection_queue.put(connection_socket1)
        connection_queue.put(connection_socket2)

except KeyboardInterrupt:
   print("\nClosing Server")
   # Closing server and join manager thread.
   manager_thread.join()
   server_socket.close()


