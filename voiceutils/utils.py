'''
voice utils for polly processing.
'''

def read_file(filename):
    with open(filename, 'r') as f:
        return f.read()


def read_csv(filename):
    import os
    import csv

    resp = []

    __is__ = False
    
    assert (os.path.exists(filename)) , "ERROR: The file '%s' does not exist." % (filename)
    with open(filename) as csv_file:
        cols = []
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
                cols = row
            else:
                line_count += 1
                num_compound = 0
                for i,r in enumerate(row):
                    if ('\n' in r):
                        row[i] = r.split('\n')
                        num_compound += 1
                    elif ('"' in r):
                        row[i] = r.replace('"', '')
                        __is__ = True
                if (num_compound > 0):
                    assert not isinstance(row[0], list), "ERROR: The first column must be a single value."
                    n = max(len(row[i]) for i in range(1,len(row)))
                    rows = []
                    for i in range(n):
                        _row = [row[0]]
                        for j in range(1, len(row)-1):
                            _row.append(row[j][i])
                        rows.append(_row)
                    for _row in rows:
                        resp.append(dict(zip(cols, _row)))
                    __is__ = True
                    continue
                _d_ = dict(list(zip(cols, row)))
                resp.append(_d_)
    return resp, __is__
    
    
def write_csv(filaneme, data):
    import csv

    with open(filaneme, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data[1:])
