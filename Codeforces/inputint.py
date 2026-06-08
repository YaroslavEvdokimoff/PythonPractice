def solve():
    a = int(input())
    for _ in range(a):
        b, c = input().split()
        b = int(b)
        d = input()
        
        for e in range(b):
            if d[e] < c:# Ищем первую цифру, которая строго меньше "c"
                print(d[:e] + c + d[e:])
                break
            
        else:           # Этот блок сработает, если подходящей цифры не нашлось 
            print(d + c)

if __name__ == '__main__':
    solve()
