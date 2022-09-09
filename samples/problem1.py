def pad_if_necessary(something, num=4):
    '''
    something is a string of up to num chars. pad if the number of chars is less than num.
    '''
    return '0'*(4-len(something)) + something

def solution(a, b, num=4):
    assert isinstance(a, list), 'a is not a list'
    assert isinstance(b, list), 'b is not a list'
    assert len([n for n in a if (len(str(n)) <= 4)]) == len(a), 'data for a is not correct. expected a list of 4 digit items.'
    assert len([n for n in b if (len(str(n)) <= 4)]) == len(b), 'data for b is not correct. expected a list of 4 digit items.'
    a_value = int(''.join([pad_if_necessary(str(n)) for n in a]))
    b_value = int(''.join([pad_if_necessary(str(n)) for n in b]))
    x_value = a_value + b_value
    r = len(str(x_value)) % num
    p = num - r
    x_value = '0'*p + str(x_value) if (r > 0) else x_value
    return [int(str(x_value)[i:i+4]) for i in range(0, len(str(x_value)), 4)]

a =  [9876, 5432, 1999]
b = [1, 8001]

x = solution(a, b)
print(x)

expected = [9876, 5434, 0]
print(expected)

assert x == expected, 'expected %s, got %s' % (expected, x)

a= [123, 4, 5] 
b = [100, 100, 100]
expected = [223, 104, 105]

x = solution(a, b)
print(x)

print(expected)

assert x == expected, 'expected %s, got %s' % (expected, x)
