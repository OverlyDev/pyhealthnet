# pyHealthNet

Definitely a work-in-progress.

General idea:

- one server
- many clients
- clients register with server
- clients send heartbeats to server
- server knows when(ish) to expect heartbeats
- client doesn't respond when expected, or sends bad status, server sends notification
