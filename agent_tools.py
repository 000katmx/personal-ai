"""
agent_tools.py – Tool definitions for the Personal AI Assistant.
Uses duckduckgo-search for web queries and psutil for system diagnostics.
"""

import platform
import subprocess
from typing import List, Dict, Optional

from duckduckgo_search import DDGS
from langchain.tools import tool
import psutil


@tool
def web_search(query: str, max_results: int = 5) -> str:
    """
    Perform a real-time web search using DuckDuckGo.
    
    Args:
        query: The search query string.
        max_results: Maximum number of results to return (default: 5).
    
    Returns:
        Formatted string with search results including titles, snippets, and sources.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            
            if not results:
                return "❌ No results found for your query."
            
            formatted_results = []
            for i, r in enumerate(results[:max_results], 1):
                title = r.get('title', 'No title')
                body = r.get('body', 'No description')
                href = r.get('href', 'No URL')
                formatted_results.append(
                    f"{i}. **{title}**\n"
                    f"   {body[:300]}{'...' if len(body) > 300 else ''}\n"
                    f"   🔗 {href}\n"
                )
            
            return f"🔍 Search results for '{query}':\n\n" + "\n".join(formatted_results)
    
    except Exception as e:
        return f"❌ Web search failed: {str(e)}"


@tool
def get_system_info() -> str:
    """
    Retrieve comprehensive system and network diagnostics.
    
    Returns:
        Formatted string with OS details, CPU, memory, and network interface information.
    """
    try:
        info_lines = [
            "🖥️ **System Information**",
            "=" * 40,
            f"• Operating System: {platform.system()} {platform.release()}",
            f"• OS Version: {platform.version()}",
            f"• Architecture: {platform.machine()} ({platform.processor()})",
            f"• Hostname: {platform.node()}",
        ]
        
        # CPU Information
        cpu_cores = psutil.cpu_count(logical=False)
        cpu_logical = psutil.cpu_count(logical=True)
        cpu_percent = psutil.cpu_percent(interval=1)
        info_lines.extend([
            "",
            "💻 **CPU**",
            f"• Physical cores: {cpu_cores or 'Unknown'}",
            f"• Logical cores: {cpu_logical or 'Unknown'}",
            f"• Current usage: {cpu_percent}%",
            f"• Load average: {', '.join(f'{x:.2f}' for x in psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else 'N/A'}",
        ])
        
        # Memory Information
        mem = psutil.virtual_memory()
        info_lines.extend([
            "",
            "🧠 **Memory**",
            f"• Total: {mem.total / (1024**3):.2f} GB",
            f"• Available: {mem.available / (1024**3):.2f} GB",
            f"• Used: {mem.used / (1024**3):.2f} GB ({mem.percent}%)",
            f"• Swap total: {psutil.swap_memory().total / (1024**3):.2f} GB" if psutil.swap_memory() else "• Swap: N/A",
        ])
        
        # Disk Information
        disk = psutil.disk_usage('/')
        info_lines.extend([
            "",
            "💾 **Disk**",
            f"• Total: {disk.total / (1024**3):.2f} GB",
            f"• Used: {disk.used / (1024**3):.2f} GB ({disk.percent}%)",
            f"• Free: {disk.free / (1024**3):.2f} GB",
        ])
        
        # Network Interfaces
        info_lines.extend([
            "",
            "🌐 **Network Interfaces**",
        ])
        addrs = psutil.net_if_addrs()
        for iface, addr_list in addrs.items():
            # Skip loopback and virtual interfaces for cleaner output
            if iface.startswith('lo') or 'docker' in iface or 'veth' in iface:
                continue
            for addr in addr_list:
                if addr.family == 2:  # AF_INET (IPv4)
                    info_lines.append(f"• {iface}: {addr.address}")
                    if addr.netmask:
                        info_lines.append(f"  Netmask: {addr.netmask}")
                elif addr.family == 23:  # AF_INET6 (IPv6)
                    info_lines.append(f"• {iface} (IPv6): {addr.address}")
        
        # Network statistics
        net_io = psutil.net_io_counters()
        info_lines.extend([
            "",
            f"📊 **Network Traffic**",
            f"• Bytes sent: {net_io.bytes_sent / (1024**2):.2f} MB",
            f"• Bytes received: {net_io.bytes_recv / (1024**2):.2f} MB",
            f"• Packets sent: {net_io.packets_sent:,}",
            f"• Packets received: {net_io.packets_recv:,}",
        ])
        
        # Running processes count
        process_count = len(psutil.pids())
        info_lines.extend([
            "",
            f"⚙️ **Processes**",
            f"• Running processes: {process_count}",
        ])
        
        return "\n".join(info_lines)
    
    except ImportError:
        return "❌ psutil not installed. Please install it with: pip install psutil"
    except Exception as e:
        return f"❌ Error fetching system information: {str(e)}"


@tool
def network_diagnostics(target: str = "8.8.8.8", count: int = 4) -> str:
    """
    Perform basic network diagnostics (ping) to a target host.
    
    Args:
        target: The hostname or IP address to ping (default: 8.8.8.8).
        count: Number of ping packets to send (default: 4).
    
    Returns:
        Ping results as a formatted string.
    """
    try:
        # Determine ping command based on OS
        if platform.system().lower() == "windows":
            cmd = ["ping", "-n", str(count), target]
        else:  # Linux/macOS
            cmd = ["ping", "-c", str(count), target]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return f"✅ Ping to {target} successful:\n\n{result.stdout.strip()}"
        else:
            return f"❌ Ping to {target} failed:\n\n{result.stderr.strip() or result.stdout.strip()}"
    
    except subprocess.TimeoutExpired:
        return f"❌ Ping to {target} timed out after 10 seconds."
    except Exception as e:
        return f"❌ Network diagnostics failed: {str(e)}"