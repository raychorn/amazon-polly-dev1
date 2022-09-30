'''
[2:25 PM] Arokiasamy, John
Write a function to accept a list of integers and return a list of integers. The every element in the output is a product (multiply elements) of all elements in the input list except the 
element in the same position as the index.

[2:25 PM] Arokiasamy, John
sample input = [1,2,34]
sample output = [24,12,8,6]


sample input = [1,2,3,4]
sample output = [24,12,8,6]

index=1
[1,2,3,4]
[24,12,8,6]

index=2
[1,2,3,4]
[24,12,8,6]

index=3
[1,2,3,4]
[24,12,8,6]

index=4
[1,2,3,4]
[24,12,8,6]

'''

l = [0,1,2,3,4,5,6,7,8,9]

class DebugSomthing:
    def __init__(self, function, func=None):
        self.function = function
     
    def __call__(self, *args, **kwargs):
        bar = self.function(*args, **kwargs)
        print(bar)
 
 
@DebugSomthing(func=print)
def foo(ll=[]):
    resp = []
    for i,v in enumerate(ll):
        vals = set(l) - set([v])
        m = 1
        for n in vals:
            m *= n
        resp.append(m)
    return resp
        

l = [1,2,3,4]
x = foo(l)
