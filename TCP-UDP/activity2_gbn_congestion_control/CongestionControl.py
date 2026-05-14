class CongestionControl:
    SLOW_START = "slow_start"
    CONGESTION_AVOIDANCE = "congestion_avoidance"

    def __init__(self, MSS: int):
        self.MSS = MSS
        self.cwnd = MSS
        self.ssthresh = None
        self.current_state = self.SLOW_START

    def get_cwnd(self):
        return self.cwnd

    def get_MSS_in_cwnd(self):
        return self.cwnd // self.MSS

    def get_ssthresh(self):
        return self.ssthresh

    def is_state_slow_start(self):
        return self.current_state == self.SLOW_START

    def is_state_congestion_avoidance(self):
        return self.current_state == self.CONGESTION_AVOIDANCE

    def event_ack_received(self):
        if self.current_state == self.SLOW_START:
            self.cwnd += self.MSS

            if self.ssthresh is not None and self.cwnd >= self.ssthresh:
                self.current_state = self.CONGESTION_AVOIDANCE

        elif self.current_state == self.CONGESTION_AVOIDANCE:
            increment = self.MSS / self.get_MSS_in_cwnd()
            self.cwnd += int(increment)

    def event_timeout(self):
        self.ssthresh = max(self.cwnd // 2, self.MSS)
        self.cwnd = self.MSS
        self.current_state = self.SLOW_START

    def __str__(self):
        return (
            f"CongestionControl("
            f"state={self.current_state}, "
            f"cwnd={self.cwnd}B ({self.get_MSS_in_cwnd()} MSS), "
            f"ssthresh={self.ssthresh}B, "
            f"MSS={self.MSS}B)"
        )
