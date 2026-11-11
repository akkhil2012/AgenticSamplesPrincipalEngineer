"""One-command launcher: local A2A service + Streamlit, cleaned up on exit."""

import os
import subprocess
import sys
import time
import urllib.request

from catalog import ROOT
from dotenv import load_dotenv


def main():
    load_dotenv(ROOT / ".env")
    if not os.getenv("OPENAI_API_KEY"):
        sys.exit("Set OPENAI_API_KEY in .env first. There is no mock fallback.")
    port = int(os.getenv("UI_PORT", "8502"))
    processes = []
    try:
        processes.append(
            subprocess.Popen(
                [sys.executable, str(ROOT / "specialist_server.py")], cwd=ROOT
            )
        )
        # Do not accidentally attach the UI to an unrelated service already using 9001.
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        ready = False
        for _ in range(50):
            if processes[0].poll() is not None:
                sys.exit(
                    "Specialist could not start; check whether port 9001 is already in use."
                )
            try:
                with opener.open(
                    "http://127.0.0.1:9001/.well-known/agent-card.json", timeout=1
                ):
                    ready = True
                    break
            except OSError:
                time.sleep(0.1)
        if not ready:
            sys.exit("Specialist startup timed out.")
        processes.append(
            subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "streamlit",
                    "run",
                    str(ROOT / "app.py"),
                    "--server.address",
                    "127.0.0.1",
                    "--server.port",
                    str(port),
                    "--browser.gatherUsageStats",
                    "false",
                ],
                cwd=ROOT,
            )
        )
        print(
            f"Open http://localhost:{port}. Press Ctrl+C to stop both services.",
            flush=True,
        )
        while all(p.poll() is None for p in processes):
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        for process in reversed(processes):
            if process.poll() is None:
                process.terminate()
        for process in processes:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


if __name__ == "__main__":
    main()
