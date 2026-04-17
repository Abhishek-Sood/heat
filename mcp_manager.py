#!/usr/bin/env python3
"""
MCP Server Management Script
Helps you properly start/stop MCP server and understand what's running
"""

import subprocess
import sys
import psutil
import time

def find_mcp_processes():
    """Find all MCP-related Python processes"""
    mcp_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'python.exe' or proc.info['name'] == 'python':
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if 'mcp' in cmdline.lower():
                    mcp_processes.append({
                        'pid': proc.info['pid'],
                        'cmdline': cmdline
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return mcp_processes

def kill_all_mcp_processes():
    """Kill all MCP-related processes"""
    processes = find_mcp_processes()
    if not processes:
        print("✅ No MCP processes found running")
        return
    
    for proc in processes:
        try:
            print(f"🔪 Killing MCP process PID {proc['pid']}: {proc['cmdline']}")
            psutil.Process(proc['pid']).terminate()
            time.sleep(1)
            if psutil.pid_exists(proc['pid']):
                psutil.Process(proc['pid']).kill()
        except Exception as e:
            print(f"❌ Failed to kill process {proc['pid']}: {e}")

def start_mcp_server():
    """Start MCP server properly"""
    print("🚀 Starting MCP Server...")
    
    # Change to backend directory and start MCP server
    cmd = [
        sys.executable, "-m", "app.mcp.mcp_http_server"
    ]
    
    try:
        # Start in background
        process = subprocess.Popen(
            cmd,
            cwd="./backend",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"✅ MCP Server started with PID: {process.pid}")
        print("   Access MCP at: http://localhost:9000/health")
        return process
    except Exception as e:
        print(f"❌ Failed to start MCP server: {e}")
        return None

def check_mcp_status():
    """Check if MCP server is responding"""
    import requests
    try:
        response = requests.get("http://localhost:9000/health", timeout=5)
        if response.status_code == 200:
            print("✅ MCP Server is running and responding")
            return True
        else:
            print(f"❌ MCP Server responding with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ MCP Server not responding: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("""
MCP Server Manager
Usage:
  python mcp_manager.py status   - Check MCP server status
  python mcp_manager.py start    - Start MCP server
  python mcp_manager.py stop     - Stop all MCP processes
  python mcp_manager.py restart  - Stop and start MCP server
  python mcp_manager.py list     - List all MCP processes
        """)
        return

    command = sys.argv[1].lower()
    
    if command == "status":
        check_mcp_status()
        
    elif command == "start":
        if check_mcp_status():
            print("MCP Server already running")
        else:
            start_mcp_server()
            time.sleep(2)
            check_mcp_status()
            
    elif command == "stop":
        kill_all_mcp_processes()
        
    elif command == "restart":
        kill_all_mcp_processes()
        time.sleep(2)
        start_mcp_server()
        time.sleep(2)
        check_mcp_status()
        
    elif command == "list":
        processes = find_mcp_processes()
        if processes:
            print("🔍 Found MCP processes:")
            for proc in processes:
                print(f"  PID {proc['pid']}: {proc['cmdline']}")
        else:
            print("✅ No MCP processes found")
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()