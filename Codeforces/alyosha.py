def solve():
    n = int(input())
    a = list(map(int, input().split()))
    
    if sum(a) != 0:   # Если общая сумма не 0, берем весь массив целиком
        print("YES")
        print(1)
        print(1, n)
        return
    first_nonzero_idx = -1 # Сумма равна 0. Ищем первый элемент, который не равен 0
    for i in range(n):
        if a[i] != 0:
            first_nonzero_idx = i
            break
            
    
    if first_nonzero_idx == -1: # Если все элементы в массиве оказались нулями — разбиение невозможно
        print("NO")
    else:                       # Делим массив на две части: до первого ненулевого элемента включительно и после
        print("YES")
        print(2)
        print(1, first_nonzero_idx + 1)
        print(first_nonzero_idx + 2, n)

if __name__ == '__main__':
    solve()
