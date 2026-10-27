import socket, json, sys
def kirim(code, timeout=600):
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(timeout)
    s.connect(("127.0.0.1",9876))
    s.sendall(json.dumps({"type":"execute_code","params":{"code":code}}).encode())
    buf=b""
    while True:
        try: ch=s.recv(65536)
        except socket.timeout: break
        if not ch: break
        buf+=ch
        try: json.loads(buf.decode()); break
        except Exception: continue
    s.close()
    try: return json.loads(buf.decode())
    except Exception: return {"raw": buf.decode(errors="replace")[:2000]}
if __name__=="__main__":
    r=kirim(sys.stdin.read())
    if r.get("status")=="success": print(r.get("result",{}).get("result",""))
    else: print("ERROR:", json.dumps(r)[:3000])
