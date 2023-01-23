import copy

def bubblesort(input_array):
    new_array=copy.deepcopy(input_array)
    n = len(new_array)
    flag=True
    counts=0
    while (n>1) and (flag==True):
        print (new_array)
        flag = False
        for i in range(1,n):
            counts+=1
            if (new_array[i-1] > new_array[i]):
                new_array[i-1], new_array[i] = new_array[i], new_array[i-1]
                flag = True
        n-=1
    return (new_array)