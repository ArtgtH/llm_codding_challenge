import time


class RateLimiter:
    def __init__(self, rate: float):
        self.rate = rate
        self.last_request_time = 0.0

    def wait(self) -> None:
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < 1 / self.rate:
            time.sleep(1 / self.rate - time_since_last)
        self.last_request_time = time.time()
