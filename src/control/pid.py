from src.control.pid import PID

def test_pid_zero_error():
    pid = PID(1.0)
    assert pid.update(0.0, 0.1) == 0.0