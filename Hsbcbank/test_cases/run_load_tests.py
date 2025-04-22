
import subprocess
import time

def run_load_test(users, spawn_rate, duration):
    print(f"\nRunning test with {users} users, spawn rate {spawn_rate}, duration {duration}")
    cmd = f"locust -f test_cases/test_load.py --headless -u {users} -r {spawn_rate} --run-time {duration}"
    subprocess.run(cmd.split())
    time.sleep(2)  # Brief pause between tests

def main():
    # Light load test
    run_load_test(50, 10, "1m")
    
    # Medium load test
    run_load_test(200, 20, "2m")
    
    # Heavy load test
    run_load_test(500, 50, "3m")

if __name__ == "__main__":
    main()
