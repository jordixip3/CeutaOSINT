import argparse
import sys
from engine.agent_loop import CeutaOSINTAgent
from api_server import app

def main():
    parser = argparse.ArgumentParser(description="CeutaOSINT - Cyber Intelligence OSINT Suite")
    parser.add_argument("--agent", action="store_true", help="Run autonomous OSINT agent loop only")
    parser.add_argument("--serve", action="store_true", help="Start Flask API and Dashboard web server only")
    parser.add_argument("--port", type=int, default=5000, help="Web server port (default: 5000)")

    args = parser.parse_args()

    if args.agent:
        print("[*] Launching CeutaOSINT Autonomous Agent Loop...")
        agent = CeutaOSINTAgent()
        agent.run_agent_loop()
    elif args.serve:
        print(f"[*] Starting CeutaOSINT Dashboard Web Server on http://localhost:{args.port}...")
        app.run(host="0.0.0.0", port=args.port, debug=False)
    else:
        print("[*] Initializing CeutaOSINT Agent Loop & Starting Dashboard Server...")
        agent = CeutaOSINTAgent()
        agent.run_agent_loop()

        print(f"\n[🚀 SERVER READY] Access CeutaOSINT Web Dashboard at: http://localhost:{args.port}")
        app.run(host="0.0.0.0", port=args.port, debug=False)

if __name__ == "__main__":
    main()
