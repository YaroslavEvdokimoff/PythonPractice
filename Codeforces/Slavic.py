import math

def solve():
    a = int(input())
    for _ in range(a):
        b = int(input())
        c = list(map(int, input().split()))
        
        
        min_idx = c.index(min(c))# Находим индекс минимального элемента 
        c[min_idx] += 1 # Увеличиваем на 1
        
        
        print(math.prod(c))# Вычисляем произведение через math.prod

if __name__ == '__main__':
    solve()
