"""show.py ID START END  -> print litlib-numbered lines START..END (1-based)"""
import sys; sys.path.insert(0, r"D:\Research-Publishing\13-bengaluru-lakes\code")
from litlib import lines
L = lines(sys.argv[1]); a, b = int(sys.argv[2]), int(sys.argv[3]); w = int(sys.argv[4]) if len(sys.argv) > 4 else 200
for i in range(a - 1, min(b, len(L))): 
    if L[i].strip(): print(i + 1, L[i][:w])
