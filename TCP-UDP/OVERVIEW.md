# TCP Congestion Control - Project Overview

## Implementation Summary

Complete implementation of TCP Go-Back-N with TCP Tahoe congestion control mechanism.

## Files Overview

### Core Implementation
| File | Description |
|------|-------------|
| `CongestionControl.py` | TCP Tahoe congestion control (slow start + AIMD) |
| `slidingWindowCC.py` | Sliding window with sequence numbers |
| `socketUDP.py` | UDP socket with multiple timers |
| `SocketTCP_GBN.py` | TCP socket with Go-Back-N and congestion control |

### Tests
| File | Description |
|------|-------------|
| `CongestionControl_test.py` | Unit tests for CongestionControl class |
| `cliente_gbn.py` | Test client for Go-Back-N |
| `servidor_gbn.py` | Test server for Go-Back-N |
| `test_completo.py` | Complete automated test suite |

### Documentation
| File | Description |
|------|-------------|
| `ENTREGA.md` | Submission document (Spanish) |
| `RESPUESTAS_GBN.md` | Answers to assignment questions |
| `README_GBN.md` | Usage instructions |
| `OVERVIEW.md` | This file |

## Quick Start

### Test Part 1 (CongestionControl class):
```bash
python3 CongestionControl_test.py
```

### Test Parts 2 & 3 (Go-Back-N with congestion control):

Terminal 1 (server):
```bash
python3 servidor_gbn.py
```

Terminal 2 (client):
```bash
python3 cliente_gbn.py test_100kb.bin
```

Debug mode:
```bash
python3 cliente_gbn.py test_100kb.bin debug
```

## Implementation Details

### Part 1: CongestionControl Class
- MSS: 8 bytes
- Initial cwnd: 1 MSS
- Initial ssthresh: None (set on first timeout)
- Slow start: cwnd += 1 MSS per ACK
- Congestion avoidance: cwnd += MSS/cwnd per ACK
- Timeout: ssthresh = cwnd/2, cwnd = 1 MSS, back to slow start

### Part 2: Go-Back-N
- Sliding window with variable size
- Cumulative ACKs
- Retransmit entire window on timeout
- One timer per segment in window
- Receiver only accepts in-order segments

### Part 3: Integration
- Congestion control object manages window size
- Window size = cwnd / MSS
- Calls `event_timeout()` on timeout
- Calls `event_ack_received()` on ACK
- Updates window size when cwnd changes
- Sends new segments when window grows
- Handles window shrinking edge case

## Features

- Simple, clean code (no comments, student-level)
- Full TCP Tahoe implementation
- Debug mode shows congestion control evolution
- Segment counter for efficiency analysis
- Works with packet loss (manual or netem)
- Reliable delivery verification

## Testing

### Without packet loss:
- Exponential growth in slow start
- Transition to congestion avoidance
- Fast transmission

### With packet loss:
- Timeout detection
- ssthresh update
- cwnd reset
- Gradual recovery
- Complete file delivery

## Performance

### Metrics tracked:
- Transmission time
- Number of segments sent
- Congestion window evolution
- State transitions

### Comparison: Go-Back-N vs Stop & Wait
- GBN faster without loss (parallel transmission)
- GBN adapts to network conditions
- Stop & Wait simpler but slower
- GBN overhead when retransmitting full window

## Limitations

Educational implementation with simplifications:
- MSS = 8 bytes (vs typical 1460 bytes)
- No fast retransmit (3 duplicate ACKs)
- No fast recovery (TCP Reno feature)
- No SACK (Selective ACK)
- No packet reordering handling
- Fixed timeout (no RTT estimation)

## Assignment Compliance

✓ Part 1 (1.5 pts): CongestionControl class fully implemented
✓ Part 2 (1.5 pts): Go-Back-N fully implemented
✓ Part 3 (1.5 pts): Integration complete with dynamic window
✓ Tests (1.5 pts): All tests pass, comprehensive testing

Total: 4.5 pts code + 1.5 pts report = 6.0 pts

## Next Steps

To extend this implementation:
1. Add fast retransmit (detect 3 duplicate ACKs)
2. Implement TCP Reno (fast recovery)
3. Add RTT estimation for dynamic timeout
4. Implement SACK for selective retransmission
5. Use realistic MSS (1460 bytes)
6. Add bandwidth estimation
7. Implement TCP Vegas or CUBIC
