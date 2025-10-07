#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unified startup script for all backend services
Starts all FastAPI services on different ports
"""

import subprocess
import sys
import time
from pathlib import Path

# Ensure UTF-8 encoding for console output on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Get the project root directory (parent of scripts/)
PROJECT_ROOT = Path(__file__).parent.parent

# Service configurations
SERVICES = [
    {
        "name": "Document Converter",
        "file": "backend.services.document_converter",
        "port": 8000,
        "host": "127.0.0.1"
    },
    {
        "name": "Sentiment Analysis",
        "file": "backend.services.sentiment_service",
        "port": 8001,
        "host": "127.0.0.1"
    },
    {
        "name": "NER Service",
        "file": "backend.services.ner_service",
        "port": 8002,
        "host": "127.0.0.1"
    },
    {
        "name": "LangExtract Service",
        "file": "backend.services.langextract_service",
        "port": 8003,
        "host": "127.0.0.1"
    }
]

def main():
    print("=" * 60)
    print("🚀 Starting FinSight Backend Services")
    print("=" * 60)

    processes = []

    try:
        for service in SERVICES:
            print(f"\n📦 Starting {service['name']} on port {service['port']}...")

            # Start the service using uvicorn
            # Only watch the backend directory to avoid .venv and node_modules
            cmd = [
                sys.executable,
                "-m", "uvicorn",
                f"{service['file']}:app",
                "--host", service['host'],
                "--port", str(service['port']),
                "--reload",
                "--reload-dir", str(PROJECT_ROOT / "backend")
            ]

            # Don't capture output - let it print to console
            process = subprocess.Popen(
                cmd,
                cwd=str(PROJECT_ROOT)
            )

            processes.append({
                "name": service['name'],
                "process": process,
                "port": service['port']
            })

            # Give it a moment to start
            time.sleep(2)

        print("\n" + "=" * 60)
        print("✅ All services started successfully!")
        print("=" * 60)
        print("\n📍 Running services:")
        for p in processes:
            print(f"  • {p['name']}: http://127.0.0.1:{p['port']}")

        print("\n📚 API Documentation:")
        for p in processes:
            print(f"  • {p['name']}: http://127.0.0.1:{p['port']}/docs")

        print("\n⚠️  Press Ctrl+C to stop all services")
        print("=" * 60)
        print("\n💡 Waiting for models to load... Check logs above\n")

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
