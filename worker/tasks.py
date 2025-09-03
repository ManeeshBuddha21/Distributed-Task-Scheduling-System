
def do_echo(payload):
    return {"echo": payload}

def do_upper(payload):
    text = str(payload.get("text",""))
    return {"upper": text.upper()}

def fib(n: int) -> int:
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b

def do_fib(payload):
    n = int(payload.get("n", 20))
    return {"fib": fib(n), "n": n}
