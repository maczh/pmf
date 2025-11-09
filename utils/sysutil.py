import subprocess
import time
from threading import Timer

def cmd_exec(name: str, *args) -> tuple[str, Exception]:
    """执行系统命令"""
    try:
        result = subprocess.run([name] + list(args), capture_output=True, text=True, check=True)
        return result.stdout, None
    except Exception as e:
        return "", e

def cmd_run_with_timeout(cmd: list[str], timeout: float) -> tuple[Exception, bool]:
    """带超时的命令执行"""
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    timer = Timer(timeout, proc.kill)
    
    try:
        timer.start()
        stdout, stderr = proc.communicate()
        if proc.returncode != 0:
            return Exception(stderr.decode()), False
        return None, False
    except Exception as e:
        return e, False
    finally:
        timer.cancel()