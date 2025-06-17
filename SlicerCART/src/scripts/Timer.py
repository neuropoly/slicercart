import time

from utils.constants import TIMER_MUTEX


class Timer():
    # @enter_function
    def __init__(self, number=None):
        """
        __init__

        Args:
            number: Description of number.
        """
        with TIMER_MUTEX:
            self.number = number
            self.total_time = 0
            self.inter_time = 0
            # counting flag to allow to PAUSE the time
            # False = not counting, True = counting (for pause button)
            self.flag = False

    # @enter_function
    def start(self):
        """
        start

        Args:
        """
        with TIMER_MUTEX:
            if self.flag == False:
                # start counting flag (to allow to pause the time if False)
                self.flag = True
                self.start_time = time.time()

    # @enter_function
    def stop(self):
        """
        stop

        Args:
        """
        with TIMER_MUTEX:
            if self.flag == True:
                self.inter_time = time.time() - self.start_time
                self.total_time += self.inter_time
                self.flag = False