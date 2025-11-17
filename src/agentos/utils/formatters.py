from typing import Any
from datetime import timedelta

def format_bytes(bytes_value: int) -> str:
    """Format bytes as human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"

def format_duration(seconds: float) -> str:
    """Format duration in seconds as human-readable string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    
    duration = timedelta(seconds=int(seconds))
    
    parts = []
    if duration.days > 0:
        parts.append(f"{duration.days}d")
    
    hours = duration.seconds // 3600
    if hours > 0:
        parts.append(f"{hours}h")
    
    minutes = (duration.seconds % 3600) // 60
    if minutes > 0:
        parts.append(f"{minutes}m")
    
    seconds_part = duration.seconds % 60
    if seconds_part > 0 or not parts:
        parts.append(f"{seconds_part}s")
    
    return " ".join(parts)

def format_table(data: list[dict], headers: list[str]) -> str:
    """Format data as ASCII table."""
    if not data:
        return "No data"
    
    # Calculate column widths
    widths = {h: len(h) for h in headers}
    for row in data:
        for header in headers:
            value = str(row.get(header, ""))
            widths[header] = max(widths[header], len(value))
    
    # Build table
    lines = []
    
    # Header
    header_line = " | ".join(h.ljust(widths[h]) for h in headers)
    lines.append(header_line)
    lines.append("-" * len(header_line))
    
    # Rows
    for row in data:
        row_line = " | ".join(
            str(row.get(h, "")).ljust(widths[h]) 
            for h in headers
        )
        lines.append(row_line)
    
    return "\n".join(lines)
