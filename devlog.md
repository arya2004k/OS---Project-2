Sunday, November 1, 2025 – 3:10 PM

Today I finally sat down and started reading through the Project 2 instructions. The whole project is about simulating a bank with multiple tellers, customers, a manager, and even a safe, so everyone has to sync correctly using semaphores and threads. It looks difficult because there are like a million steps each customer and teller has to follow.

I created my new project folder and made a starting Python file. I named it bank.py to keep everything clean. My only goal for today was to understand the flowchart in the instructions and figure out how many semaphores I need. I wrote down a list: one for the safe (only 2 tellers allowed inside), one for the manager (only 1 teller can talk to them), and one for the door (only 2 customers can enter at once). I think I’ll build the teller thread first next time.

Monday, November 2, 2025 – 8:40 PM

Today I worked on the teller logic. I made the teller thread announce that it’s ready, wait for customers, and then call the next customer from the queue. At this point, the code doesn’t really do anything useful, but at least it runs without crashing.

I also added print locking because the instructions said the output format has to be super specific. I was confused at first about how to handle the bracket formatting, like Teller 0 [Customer 5]: message, but I added a helper function called log() so all threads use the same printing style.

My next plan is to write the CustomerContext object because there are soooo many signals between a customer and a teller.

Tuesday, November 3, 2025 – 7:55 PM

Today I focused on building CustomerContext. This project has so many semaphores inside just one customer—one for being called, one for introduction, one for transaction asked, one for being done, etc.

When I tried running it, everything deadlocked immediately. I forgot to actually release the called_by_teller semaphore, so the customers waited forever. Once I fixed that, the program finally started showing output… but it's still very broken.

Tomorrow I’ll build the actual customer behavior step by step.

Thursday, November 5, 2025 – 6:25 PM

I worked on customer behavior today. Customers pick randomly between deposit and withdrawal, wait a random 0–100 ms, and then wait for the bank to open. After that, they enter through the door. My issue is that now all my code does is spit out all the output at once.

At first, customers were skipping steps. I realized it was because customers were entering the queue before the tellers were counted as “waiting,” so they always thought a teller was ready even when none were. I wrapped the ready counter with a lock and fixed it to the best of my ability.

Next time, I want to implement the safe and the manager interactions and see if I can fix the output.

Friday, November 6, 2025 – 9:40 PM

Added safe and manager logic. This part was definitely confusing. Withdrawals must go to the manager before going to the safe. Deposits go straight to the safe.

When I ran it, the output lines got mixed up because the string inside the safe logs didn’t match the instructions exactly. I rewrote them to match the assignment’s exact phrasing, like “waiting while performing a transaction in a safe.”

Now the threads run, but everything is out of order, and the entire output is still generated. I think the problem is my queue handling.

Sunday, November 8, 2025 – 4:15 PM

Today was all debugging. Customers were getting called by tellers too early or too late. I found out that the teller was popping from the queue before checking for a sentinel value, which made the program act weird.

I also added a flush to all prints (even though Python flushes pretty well on its own) just to make the simulator behave more consistently.

I’m still having issues with the customer flow, printing everything way too fast, and sometimes overlapping. I’ll keep fixing it tomorrow.

Tuesday, November 10, 2025 – 8:30 PM

Worked on synchronizing the customer introduction → teller asks → customer replies chain. One bug I fixed: customers would “hear” the teller ask before the teller actually printed the message. I fixed the ordering so logs appear exactly in the right sequence.

The simulation finally runs without freezing, but the output is still extremely long. I think this is normal because the instructions said the program must generate a lot of output.

I’m going to refine all the messages tomorrow so they're all correct.

Thursday, November 12, 2025 – 9:55 PM

Added sentinel logic so tellers stop correctly when all customers finish. Before this, tellers kept waiting forever after the last customer.

I also tested with many customer counts, like 5, 10, and 2,0 before finally going to 50. Everything still worked, but the output printed too fast and felt instant. I realized that’s normal in a multithreaded simulation unless I add artificial delays.

Everything is becoming consistent, but everything is being outputted at once. I’ll make the README next.

Saturday, November 14, 2025 – 6:10 PM

Made the README today! I explained how the program works, what the threads do, and how to run it with python3 bank.py.

I also cleaned up my final code: removed leftover debug prints, renamed some variables, improved comments, and organized logs in the correct format.

Sunday, November 16, 2025 – 8:20 PM

Everything is done for the most part. I ran the full simulation multiple times, and it outputs everything still, with tellers calling customers, manager interactions, safe interactions, and customers leaving through the door.

I tested different seeds and customer counts, and nothing crashed, so my best choice is to submit this. 
