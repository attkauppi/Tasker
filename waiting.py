from random import random
import threading
from threading import *
import time

progress = 0
result = None
result_available = threading.Event()

def background_calculation():
    """ Some long calculation """
    time.sleep(random() * 5 * 60)

    # Waiting with "progress bar"
    global progress
    for i in range(100):
        time.sleep(random() * 3)
        progress = i + 1



    # When calculation is done, the result is stored in a
    # global variable
    global result
    result = 42
    result_available.set()

    time.sleep(10)


def main():
    thread = threading.Thread(target=background_calculation)
    thread.start()

    # TODO wait for the result to be available before continuing
    
    # wait here for the result to be available before continuing
    # thread.join()
    # Wait for event
    # result_available.wait()
    # Same as before, but now we see progress
    while not result_available(timeout=5):
        print('\r{}% done...'.format(progress), end='', flush=True)
    print('\r{}% done...'.format(progress))


    print("The result is: ", result)


if __name__ == '__main__':
    main()