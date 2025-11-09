def display_size(raw: float) -> str:
    """将字节大小转换为人类可读的格式（B/K/M/G/T/P/E）"""
    if raw < 1024:
        return f"{raw:.1f}B"
    elif raw < 1024 * 1024:
        return f"{raw / 1024:.1f}K"
    elif raw < 1024 * 1024 * 1024:
        return f"{raw / (1024 * 1024):.1f}M"
    elif raw < 1024 * 1024 * 1024 * 1024:
        return f"{raw / (1024 * 1024 * 1024):.1f}G"
    elif raw < 1024 * 1024 * 1024 * 1024 * 1024:
        return f"{raw / (1024 **4):.1f}T"
    elif raw < 1024 * 1024 * 1024 * 1024 * 1024 * 1024:
        return f"{raw / (1024** 5):.1f}P"
    elif raw < 1024 * 1024 * 1024 * 1024 * 1024 * 1024 * 1024:
        return f"{raw / (1024 **6):.1f}E"
    else:
        return "TooLarge"