X=[2]
for i in X:
    a=i
    print(X)
    print(i)
    if type(i) == int:
        X.append('a')
        print(X)
    X.remove(a)
    print(X)
    print('ok')