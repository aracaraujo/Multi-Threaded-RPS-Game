from socket import *
import sys

server_name = 'localhost'
server_port = 6789

client_socket = socket(AF_INET, SOCK_STREAM)
INPUTS = ['R','P','S','Q','r','p','s','q']

try:
    # Connecting to server.
    client_socket.connect((server_name, server_port))

    name = input("What is your name? ")

    client_socket.send(name.encode('UTF-8'))

    # Receing the oponents name.
    oponent = client_socket.recv(1024).decode('UTF-8')
    if oponent == 'Q':
        print('Oponent quit the game.')
        sys.exit(1)

    print("Welcome to Rock, Paper, and Scissors game.")
    print(f'You are playing against {oponent}')

    # Game loop.
    while True:
        
        inputChecker = False

        while not inputChecker:

            # Getting user move.
            userMove = input("What is your move? R,P,S, or Q to quit. ")

            if userMove not in INPUTS:
                print("Invalid input. Try again.\n")
            else:
                client_socket.send(userMove.upper().encode('UTF-8'))
                inputChecker = True

        # Receving results back from the server.
        result = []
        while len(result) < 3:
            for char in client_socket.recv(1024).decode('UTF-8'):
                result.append(char)

        # Checking the results and printing to the user.
        if result[0] == 'Q':
            print("The other player left the game.\nThe final score is:\n")
            print(f'Score: \nYou: {result[1]}\n{oponent}: {result[2]}')
            break
        if result[0] == 'W':
            print('You Won.')
        elif result[0] == 'L':
            print('You Lost.')
        elif result[0] == 'T':
            print('It was a tie.')
        print(f'Score: \nYou: {result[1]}\n{oponent}: {result[2]}')

        # Checking who won the game.
        if int(result[1]) == 9:
            print("\nCongratulations! You won the game.")
            print(f'Final Score: \nYou: {result[1]}\n{oponent}: {result[2]}')
            break
        if int(result[2]) == 9:
            print("\nUnfortunately you lost the game. Good luck next time.")
            print(f'Final Score: \nYou: {result[1]}\n{oponent}: {result[2]}')
            break
    
    # Closing the game.
    print("\nClosing game.")
    client_socket.close()

# Handling exceptions.
except KeyboardInterrupt:
   print("\nClosing game.")
   client_socket.send('Q'.upper().encode('UTF-8'))
   client_socket.close()

except ConnectionRefusedError:
    print("Server is offline or incorrect port number.")
