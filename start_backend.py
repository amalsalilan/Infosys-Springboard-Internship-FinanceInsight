#!/usr/bin/env python
"""
Unified startup script for all backend services
Starts all FastAPI services on different ports
"""

import subprocess
import sys
import time
from pathlib import Path

# Service configurations
SERVICES = [
    {
        "name": "Document Converter",
        "file": "document_converter.py",
        "port": 8000,
        "host": "127.0.0.1"
    },
    {
        "name": "Sentiment Analysis",
        "file": "sentiment_service.py",
        "port": 8001,
        "host": "127.0.0.1"
    },
    {
        "name": "NER Service",
        "file": "ner_service.py",
        "port": 8002,
        "host": "127.0.0.1"
    },
    {
        "name": "LangExtract Service",
        "file": "langextract_service.py",
        "port": 8003,
        "host": "127.0.0.1"
    }
]

def main():
    print("=" * 60)
    print("Starting FinSight Backend Services")
    print("=" * 60)

    processes = []

    try:
        for service in SERVICES:
            print(f"\n🚀 Starting {service['name']} on http://{service['host']}:{service['port']}")

            # Start the service using uvicorn
            cmd = [
                "uvicorn",
                f"{Path(service['file']).stem}:app",
                "--host", service['host'],
                "--port", str(service['port']),
                "--reload"
            ]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            processes.append({
                "name": service['name'],
                "process": process,
                "port": service['port']
            })

            # Give it a moment to start
            time.sleep(1)

        print("\n" + "=" * 60)
        print("✅ All services started successfully!")
        print("=" * 60)
        print("\nRunning services:")
        for p in processes:
            print(f"  • {p['name']}: http://127.0.0.1:{p['port']}")

        print("\n📝 API Documentation:")
        for p in processes:
            print(f"  • {p['name']}: http://127.0.0.1:{p['port']}/docs")

        print("\n⚠️  Press Ctrl+C to stop all services\n")

        # Wait for all processes
        while True:
            time.sleep(1)
            # Check if any process has died
            for p in processes:
                if p['process'].poll() is not None:
                    print(f"\n❌ {p['name']} has stopped unexpectedly!")
                    raise KeyboardInterrupt

    except KeyboardInterrupt:
        print("\n\n🛑 Stopping all services...")
        for p in processes:
            print(f"  Stopping {p['name']}...")
            p['process'].terminate()
            try:
                p['process'].wait(timeout=5)
            except subprocess.TimeoutExpired:
                p['process'].kill()
        print("\n✅ All services stopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()
