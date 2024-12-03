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
        all_patterns = sorted(list(set(["".join(sorted(s)) for s in P[0]])), key=len)  # Ensure unique patterns
        min_length = len(all_patterns[0])
        return [s for s in all_patterns if len(s) == min_length]

    def __distribute(self, A, B):
        result = set()  # Use a set to eliminate duplicates
        for i in range(len(A)):
            for j in range(len(B)):
                if B[j] in A[i]:
                    result.add(A[i])
                else:
                    result.add(f"{A[i]}{B[j]}")
        return list(result)

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

# Utility functions remain unchanged
def refine(my_list, dc_list):
    return [i for i in my_list if int(i) not in dc_list]

def findEPI(chart):
    res = []
    for i in chart:
        if len(chart[i]) == 1:
            if chart[i][0] not in res:
                res.append(chart[i][0])
    return res

def findVariables(x):
    var_list = []
    for i in range(len(x)):
        if x[i] == '0':
            var_list.append(chr(i + 65) + "'")
        elif x[i] == '1':
            var_list.append(chr(i + 65))
    return var_list

def flatten(x):
    return [item for sublist in x.values() for item in sublist]

def findminterms(a):
    gaps = a.count('-')
    if gaps == 0:
        return [str(int(a, 2))]
    x = [bin(i)[2:].zfill(gaps) for i in range(2 ** gaps)]
    temp = []
    for i in range(2 ** gaps):
        temp2 = a[:]
        for bit in x[i]:
            temp2 = temp2.replace('-', bit, 1)
        temp.append(str(int(temp2, 2)))
    return temp

def compare(a, b):
    mismatch_index = None
    mismatch_count = 0
    for i in range(len(a)):
        if a[i] != b[i]:
            mismatch_index = i
            mismatch_count += 1
            if mismatch_count > 1:
                return False, None
    return True, mismatch_index

def removeTerms(chart, terms):
    for term in terms:
        for minterm in findminterms(term):
            chart.pop(minterm, None)

def column_dominance(chart):
    columns = list(chart.keys())
    for i in range(len(columns)):
        for j in range(i + 1, len(columns)):
            if columns[j] not in chart or columns[i] not in chart:
                continue
            if set(chart[columns[i]]) <= set(chart[columns[j]]):
                del chart[columns[i]]
                break
            elif set(chart[columns[j]]) <= set(chart[columns[i]]):
                del chart[columns[j]]
    return chart

def row_dominance(chart):
    rows = {}
    for key, implicants in chart.items():
        for implicant in implicants:
            rows.setdefault(implicant, set()).add(key)
    rows_to_remove = set()
    row_keys = list(rows.keys())
    for i in range(len(row_keys)):
        for j in range(i + 1, len(row_keys)):
            if row_keys[i] in rows_to_remove or row_keys[j] in rows_to_remove:
                continue
            if rows[row_keys[i]] <= rows[row_keys[j]]:
                rows_to_remove.add(row_keys[i])
            elif rows[row_keys[j]] <= rows[row_keys[i]]:
                rows_to_remove.add(row_keys[j])
    for row in rows_to_remove:
        for col in list(chart.keys()):
            if row in chart[col]:
                chart[col].remove(row)
    return chart

# Main Code
mt = [int(i) for i in input("Enter the minterms: ").strip().split()]
dc = [int(i) for i in input("Enter the don't cares (If any): ").strip().split()]
mt.sort()
minterms = mt + dc
minterms.sort()
size = len(bin(minterms[-1])) - 2

# Total minterms for the given size
total_minterms = set(range(2 ** size))

# Check for special cases
if set(mt) == total_minterms:
    print("Solution: F = 1")
elif set(dc) == total_minterms:
    print("Solution: F = x")
else:
    groups, all_pi = {}, set()

    # Primary Grouping
    for minterm in minterms:
        groups.setdefault(bin(minterm).count('1'), []).append(bin(minterm)[2:].zfill(size))

    # Finding Prime Implicants
    while True:
        tmp = groups.copy()
        groups, marked, should_stop = {}, set(), True
        l = sorted(list(tmp.keys()))
        for i in range(len(l) - 1):
            for j in tmp[l[i]]:
                for k in tmp[l[i + 1]]:
                    res = compare(j, k)
                    if res[0]:
                        groups.setdefault(i, []).append(j[:res[1]] + '-' + j[res[1] + 1:])
                        marked.update([j, k])
                        should_stop = False
        all_pi.update(set(flatten(tmp)) - marked)
        if should_stop:
            break

    # Prime Implicant Chart
    chart = {}
    for pi in all_pi:
        for minterm in findminterms(pi):
            if int(minterm) in mt:
                chart.setdefault(minterm, []).append(pi)

    # Finding EPIs
    EPI = findEPI(chart)
    removeTerms(chart, EPI)

    # Apply Column and Row Dominance
    chart = column_dominance(chart)
    chart = row_dominance(chart)

    # Add new EPIs after dominance
    new_epi, chart = findEPI(chart), chart
    EPI.extend(new_epi)

    # Final Simplification
    if not chart:
        # If no minterms remain, EPI covers the entire solution
        final_result = [findVariables(i) for i in EPI]
        unique_solution = set(["".join(term) for term in final_result])  # Remove duplicates
        print(f"Solution: F = {' + '.join(unique_solution)}")
    else:
        # Prepare the chart for Petrick's Method
        P = [[findVariables(j) for j in chart[i]] for i in chart if isinstance(chart[i], list)]
        final_results = Petrick(P).get()

        solutions = []
        for final_result in final_results:
            # Combine results from Petrick's Method with EPI
            combined_result = final_result + [findVariables(i) for i in EPI]

            # Flatten the combined result and remove duplicate terms
            flattened_result = ["".join(term) for term in combined_result]
            unique_terms = set(flattened_result)  # Use set to remove duplicates
            sop_expression = " + ".join(sorted(unique_terms))  # Sort for consistency

            solutions.append(sop_expression)

        # Eliminate duplicate solutions across multiple expressions
        unique_solutions = list(set(solutions))  # Use set to remove duplicates
        unique_solutions.sort()  # Optional: Sort for consistent order

        # Display only unique solutions
        for i, solution in enumerate(unique_solutions, start=1):
            print(f"Solution F{i} = {solution}")
