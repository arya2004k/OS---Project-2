
This project is my implementation of the Bank Simulation using Python threads and semaphores. The whole goal of the assignment is to model a bank with three tellers and fifty customers, and to make sure all of their interactions happen in the correct order using proper synchronization. My program follows the steps described in the instructions, including how customers enter the bank, how tellers handle transactions, and how shared resources like the safe and manager are protected.

The main file in my submission is called bank.py, which contains the complete simulation. Inside the file, I create three teller threads and fifty customer threads. The tellers all announce when they’re ready, and only when all three are ready does the bank officially open. Customers wait for the bank to open before they’re allowed inside. Once inside, only two customers may enter at a time because of the door semaphore. Customers either go directly to a ready teller or get in line and wait to be called. Every interaction between the teller and customer is controlled by semaphores to make sure the steps happen in the correct order.

The tellers follow all required steps, including talking to the manager when doing a withdrawal and going into the safe to complete the transaction. Both the manager and the safe are treated as shared resources, and I used semaphores to make sure their limits are enforced—only one teller can talk to the manager at a time, and only two can be in the safe at once. Whenever a teller sleeps to simulate time passing, I print a message before and after the sleep, just like the instructions ask us to do. Customers also follow their nine required steps, from choosing their transaction randomly to waiting for the teller to finish and then leaving the bank.

To run the program, you will enter the command python3 bank.py.

The program runs immediately and prints out all of the actions from the tellers and customers as they’re happening. Since there are 50 customers, the output is long, but that’s expected for this project.

I tried to make sure the simulation follows the assignment as closely as possible. I tested it with fewer customers first to make sure nothing deadlocked or happened out of order, and then I tested with the full set of 50 customers. Everything should run smoothly, and all threads eventually finish. Thank you for grading my project! I really tried to make it clean, readable, and as accurate as possible. 

