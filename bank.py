import threading
import time
import random
from collections import deque

NUM_TELLERS = 3
NUM_CUSTOMERS = 50           # final version must handle 50
MAX_CUSTOMER_DELAY_MS = 100  # 0–100 ms delay before going to the bank

# Semaphores for shared resources
safe_sem = threading.Semaphore(2)     # only 2 tellers in the safe at once
manager_sem = threading.Semaphore(1)  # only 1 teller can talk to the manager
door_sem = threading.Semaphore(2)     # only 2 customers can enter the door at once

# Bank opens only when all 3 tellers are ready
bank_open_event = threading.Event()

# Track when tellers are "waiting for a customer"
tellers_waiting = 0
tellers_waiting_lock = threading.Lock()

# Queue of customers waiting to be served
customer_queue = deque()
queue_lock = threading.Lock()

# Semaphore counting how many customers are waiting in line
customer_available = threading.Semaphore(0)

# For counting served customers (not strictly required for logic, but useful)
customers_served = 0
customers_served_lock = threading.Lock()

# Helper print function (thread-safe) using required format:
# THREAD_TYPE ID [THREAD_TYPE ID]: MSG
print_lock = threading.Lock()
def log(actor_type, actor_id, msg, other_type=None, other_id=None):
    if other_type is None or other_id is None:
        bracket = ""
    else:
        bracket = f"{other_type} {other_id}"
    with print_lock:
        print(f"{actor_type} {actor_id} [{bracket}]: {msg}")


class CustomerContext:
    """Per-customer synchronization and metadata."""
    def __init__(self, cid, transaction):
        self.cid = cid
        self.transaction = transaction  # "deposit" or "withdrawal"
        self.called_by_teller = threading.Semaphore(0)
        self.introduced = threading.Semaphore(0)
        self.transaction_asked = threading.Semaphore(0)
        self.transaction_done = threading.Semaphore(0)
        self.teller_id = None


def teller_thread(tid):
    """
    Teller behavior:
      - Marks itself as ready; last teller to do so opens the bank.
      - Repeatedly waits for customers, uses manager/safe as needed,
        and completes the transaction.
    """
    global tellers_waiting, customers_served

    # Mark this teller as ready for the very first time.
    # Once all 3 tellers have done this, the bank opens.
    with tellers_waiting_lock:
        if not hasattr(teller_thread, "ready_count"):
            teller_thread.ready_count = 0
        teller_thread.ready_count += 1
        log("Teller", tid, "ready to serve for the first time")

        if teller_thread.ready_count == NUM_TELLERS:
            log("Bank", "", "opens")
            bank_open_event.set()

    # Main service loop
    while True:
        # 1. Teller announces readiness
        log("Teller", tid, "ready to serve")

        # 2. Wait for a customer
        with tellers_waiting_lock:
            tellers_waiting += 1
        log("Teller", tid, "waiting for a customer")

        customer_available.acquire()
        with tellers_waiting_lock:
            tellers_waiting -= 1

        # 3. Take next customer from the line
        with queue_lock:
            ctx = customer_queue.popleft()

        # Sentinel: None means no more customers
        if ctx is None:
            log("Teller", tid, "no more customers; closing station")
            break

        ctx.teller_id = tid

        # Call the customer
        log("Teller", tid, "calls customer from line", other_type="Customer", other_id=ctx.cid)
        ctx.called_by_teller.release()

        # Wait for customer introduction
        log("Teller", tid, "waits for customer introduction", other_type="Customer", other_id=ctx.cid)
        ctx.introduced.acquire()
        log("Teller", tid, "received customer introduction", other_type="Customer", other_id=ctx.cid)

        # Ask for transaction
        log("Teller", tid, "asks for transaction", other_type="Customer", other_id=ctx.cid)
        ctx.transaction_asked.release()

        # Simulate “waiting” for the customer to say it
        log("Teller", tid, "waits for customer to tell transaction", other_type="Customer", other_id=ctx.cid)

        # If withdrawal, talk to the manager first
        if ctx.transaction == "withdrawal":
            log("Teller", tid, "going to manager for withdrawal permission", other_type="Customer", other_id=ctx.cid)
            manager_sem.acquire()
            log("Teller", tid, "talking to manager", other_type="Customer", other_id=ctx.cid)

            # time-based wait: before / after log
            log("Teller", tid, "waiting while speaking with manager", other_type="Customer", other_id=ctx.cid)
            time.sleep(random.uniform(0.01, 0.03))
            log("Teller", tid, "done speaking with manager", other_type="Customer", other_id=ctx.cid)

            manager_sem.release()
            log("Teller", tid, "leaves manager", other_type="Customer", other_id=ctx.cid)

        # Use the safe (only 2 tellers inside)
        log("Teller", tid, "going to safe", other_type="Customer", other_id=ctx.cid)
        safe_sem.acquire()
        log("Teller", tid, "using safe", other_type="Customer", other_id=ctx.cid)

        # Simulate processing time in the safe: before / after logs
        log("Teller", tid, "waiting while processing transaction in safe", other_type="Customer", other_id=ctx.cid)
        time.sleep(random.uniform(0.01, 0.05))
        log("Teller", tid, "done processing transaction in safe", other_type="Customer", other_id=ctx.cid)

        safe_sem.release()
        log("Teller", tid, "leaves safe", other_type="Customer", other_id=ctx.cid)

        # Transaction complete
        log("Teller", tid, f"completes {ctx.transaction} transaction", other_type="Customer", other_id=ctx.cid)
        ctx.transaction_done.release()

        # Count served customer
        with customers_served_lock:
            customers_served += 1


def customer_thread(cid):
    """
    Customer behavior:
      1. Randomly chooses deposit / withdrawal.
      2. Waits 0–100 ms.
      3. Waits for bank to open; enters through a door (max 2).
      4. Gets in line (or directly goes to a ready teller).
      5. Introduces itself.
      6. Waits for teller to ask for transaction and then tells the transaction.
      7. Waits for completion and leaves.
    """
    # 1. Decide random transaction
    transaction = random.choice(["deposit", "withdrawal"])
    log("Customer", cid, f"wants to perform a {transaction} transaction")

    ctx = CustomerContext(cid, transaction)

    # 2. Wait 0–100 ms before going to bank
    delay = random.uniform(0, MAX_CUSTOMER_DELAY_MS) / 1000.0
    log("Customer", cid, f"waits {int(delay * 1000)}ms before going to the bank")
    time.sleep(delay)
    log("Customer", cid, "is done waiting before going to the bank")

    # Wait until bank is open
    log("Customer", cid, "is waiting for the bank to open")
    bank_open_event.wait()
    log("Customer", cid, "sees that the bank is open")

    # 3. Enter the bank through the door (only 2 customers at a time)
    log("Customer", cid, "trying to enter the bank")
    door_sem.acquire()
    log("Customer", cid, "enters the bank")

    # 4. Get in line / go directly to ready teller
    with tellers_waiting_lock:
        free_teller = tellers_waiting > 0

    if free_teller:
        log("Customer", cid, "finds a ready teller and goes directly to line for that teller")
    else:
        log("Customer", cid, "gets in line and waits to be called")

    with queue_lock:
        customer_queue.append(ctx)
    customer_available.release()

    # 5. Wait until teller calls this customer
    ctx.called_by_teller.acquire()
    log("Customer", cid, "goes to teller", other_type="Teller", other_id=ctx.teller_id)
    log("Customer", cid, "introduces itself to teller", other_type="Teller", other_id=ctx.teller_id)
    ctx.introduced.release()

    # 6. Wait for teller to ask for transaction
    ctx.transaction_asked.acquire()
    log("Customer", cid, "hears teller ask for transaction", other_type="Teller", other_id=ctx.teller_id)

    # 7. Tell the teller the transaction
    log("Customer", cid, f"tells teller it wants to perform a {transaction} transaction",
        other_type="Teller", other_id=ctx.teller_id)

    # 8. Wait for transaction completion
    log("Customer", cid, "waits for teller to complete transaction", other_type="Teller", other_id=ctx.teller_id)
    ctx.transaction_done.acquire()
    log("Customer", cid, "sees that the transaction is complete", other_type="Teller", other_id=ctx.teller_id)

    # 9. Leave the bank
    log("Customer", cid, "leaves the bank", other_type="Teller", other_id=ctx.teller_id)
    door_sem.release()


def main():
    random.seed(0)  # deterministic-ish ordering for debugging

    # Start teller threads
    tellers = []
    for tid in range(NUM_TELLERS):
        t = threading.Thread(target=teller_thread, args=(tid,))
        t.start()
        tellers.append(t)

    # Start customer threads
    customers = []
    for cid in range(NUM_CUSTOMERS):
        c = threading.Thread(target=customer_thread, args=(cid,))
        c.start()
        customers.append(c)

    # Wait for all customers to finish (they leave the bank)
    for c in customers:
        c.join()

    # After all customers are done, send 3 sentinel "None" customers so tellers exit
    for _ in range(NUM_TELLERS):
        with queue_lock:
            customer_queue.append(None)
        customer_available.release()

    # Wait for all tellers to finish
    for t in tellers:
        t.join()

    log("Bank", "", "closes")


if __name__ == "__main__":
    main()

