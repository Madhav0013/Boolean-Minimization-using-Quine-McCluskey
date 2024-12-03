class Petrick:  # Petrick's method
    def __init__(self, P):
        self.allocated = {}
        self.P = P
        
    def get(self):
        self.P = self.__substitution(self.P)
        self.P = self.__petrick(self.P)
        self.P = self.__back_substitution(self.P)
        return self.P
    
    def __petrick(self, P):
        while len(P) > 1:
            P[0] = self.__distribute(P[0], P[1])
            del P[1]
        all_patterns = sorted(list(tuple(["".join(sorted(s)) for s in P[0]])), key=len)
        min_length = len(all_patterns[0])
        return [s for s in all_patterns if len(s) == min_length]
    
    def __distribute(self, A, B):
        result = []
        for i in range(len(A)):
            for j in range(len(B)):
                if B[j] in A[i]:
                    result.append(A[i])
                else:
                    result.append(f"{A[i]}{B[j]}")
        return result
    
    def __substitution(self, P):
        for i in range(len(P)):
            for j in range(len(P[i])):
                t = "".join(P[i][j])
                if t not in self.allocated:
                    self.allocated[chr(65 + len(self.allocated))] = t
                P[i][j] = [k for k, v in self.allocated.items() if v == t][0]
        return P
    
    def __back_substitution(self, P):
        new_P = [[0 for _ in range(len(P[i]))] for i in range(len(P))]
        for i in range(len(P)):
            for j in range(len(P[i])):
                new_P[i][j] = self.allocated[P[i][j]]
        return new_P

def refine(my_list,dc_list):
    res = []
    for i in my_list:
        if int(i) not in dc_list:
            res.append(i)
    return res

def findEPI(x):
    res = []
    for i in x:
        if len(x[i]) == 1:
            res.append(x[i][0]) if x[i][0] not in res else None
    return res

def findVariables(x):
    var_list = []
    for i in range(len(x)):
        if x[i] == '0':
            var_list.append(chr(i+65)+"'")
        elif x[i] == '1':
            var_list.append(chr(i+65))
    return var_list

def flatten(x):
    flattened_items = []
    for i in x:
        flattened_items.extend(x[i])
    return flattened_items

def findminterms(a):
    gaps = a.count('-')
    if gaps == 0:
        return [str(int(a,2))]
    x = [bin(i)[2:].zfill(gaps) for i in range(pow(2,gaps))]
    temp = []
    for i in range(pow(2,gaps)):
        temp2,ind = a[:],-1
        for j in x[0]:
            if ind != -1:
                ind = ind+temp2[ind+1:].find('-')+1
            else:
                ind = temp2[ind+1:].find('-')
            temp2 = temp2[:ind]+j+temp2[ind+1:]
        temp.append(str(int(temp2,2)))
        x.pop(0)
    return temp

def compare(a,b):
    c = 0
    for i in range(len(a)):
        if a[i] != b[i]:
            mismatch_index = i
            c += 1
            if c>1:
                return (False,None)
    return (True,mismatch_index)

def removeTerms(_chart,terms):
    for i in terms:
        for j in findminterms(i):
            try:
                del _chart[j]
            except KeyError:
                pass

def row_dominance(chart):
    keys = list(chart.keys())
    for i in keys:
        for j in keys:
            if i != j and i in chart and j in chart:
                # Ensure both i and j exist in the chart dictionary before comparing
                if set(chart[i]).issubset(set(chart[j])):
                    del chart[j]  # Remove dominated row
    return chart


def column_dominance(chart):
    keys = list(chart.keys())
    values = list(chart.values())
    for i in range(len(values)):
        for j in range(len(values)):
            if i != j and set(values[i]).issubset(values[j]):
                for key in chart.keys():
                    if values[j] in chart[key]:
                        chart[key].remove(values[j])
    return chart
mt = [int(i) for i in input("Enter the minterms: ").strip().split()]
dc = [int(i) for i in input("Enter the don't cares(If any): ").strip().split()]
mt.sort()
minterms = mt+dc
minterms.sort()
size = len(bin(minterms[-1]))-2
groups,all_pi = {},set()
for minterm in minterms:
    try:
        groups[bin(minterm).count('1')].append(bin(minterm)[2:].zfill(size))
    except KeyError:
        groups[bin(minterm).count('1')] = [bin(minterm)[2:].zfill(size)]
while True:
    tmp = groups.copy()
    groups,m,marked,should_stop = {},0,set(),True
    l = sorted(list(tmp.keys()))
    for i in range(len(l)-1):
        for j in tmp[l[i]]:
            for k in tmp[l[i+1]]:
                res = compare(j,k)
                if res[0]:
                    try:
                        groups[m].append(j[:res[1]]+'-'+j[res[1]+1:]) if j[:res[1]]+'-'+j[res[1]+1:] not in groups[m] else None
                    except KeyError:
                        groups[m] = [j[:res[1]]+'-'+j[res[1]+1:]]
                    should_stop = False
                    marked.add(j)
                    marked.add(k)
        m += 1
    local_unmarked = set(flatten(tmp)).difference(marked)
    all_pi = all_pi.union(local_unmarked)
    if should_stop:
        break
chart = {}
for i in all_pi:
    merged_minterms = findminterms(i)
    for j in refine(merged_minterms,dc):
        try:
            chart[j].append(i) if i not in chart[j] else None
        except KeyError:
            chart[j] = [i]
chart = row_dominance(chart)
chart = column_dominance(chart)
EPI = findEPI(chart)
removeTerms(chart, EPI)
if len(chart) == 0:
    final_result = [findVariables(i) for i in EPI]
    print(f"Solution: F = {' + '.join(''.join(i) for i in final_result)}")
else:
    P = [[findVariables(j) for j in chart[i]] for i in chart]
    final_results = Petrick(P).get()
    for i, final_result in enumerate(final_results):
        final_result.extend(findVariables(i) for i in EPI)
        print(f"Solution: F{i + 1} = {' + '.join(''.join(i) for i in final_result)}")
