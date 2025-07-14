

import asyncio
from refiled.cli import run_cli

def run():
    try:
        asyncio.run(run_cli())
    except KeyboardInterrupt:
        print("\n👋 Exiting gracefully...")

if __name__ == "__main__":
    run()