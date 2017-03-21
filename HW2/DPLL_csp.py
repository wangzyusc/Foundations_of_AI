"""
    This scripts is for HW2 of CS561 in Spring 2017.
    Copyright by Zhiyuan Wang since March 3rd, 2017.
"""

import operator

# global variable to keep the value assignments
solutionModel = dict()

"""
    Represent CNF as list of clauses, each clause as a list of literals,
    each literal has three components:
    [guest, table, positive] (if literal is A rather than !A, then positive is 1, or 0 o.w.)
    @:param M: number of guests
    @:param N: number of tables
    @:param R: relations between guests
"""
def getCNF(M, N, R):
    CNF = []
    #(a)
    for a in range(M):#for each guest
        clause = []
        for j in range(N):#for each table
            clause.append([a + 1, j + 1, 1])
        CNF.append(clause)
        for i in range(N):
            for j in range(i + 1, N):
                CNF.append([[a + 1, i + 1, 0], [a + 1, j + 1, 0]])
    for relation in R:
        a = relation[0]
        b = relation[1]
        if relation[2] == 'F':#(b)
            for i in range(N):
                for j in range(N):
                    if i != j:
                        CNF.append([[a, i + 1, 0], [b, j + 1, 0]])
                        CNF.append([[a, j + 1, 0], [b, i + 1, 0]])
                # CNF.append([[a, i + 1, 0], [b, i + 1, 1]])
                # CNF.append([[a, i + 1, 1], [b, i + 1, 0]])
        if relation[2] == 'E':#(c)
            for i in range(N):
                CNF.append([[a, i + 1, 0], [b, i + 1, 0]])
    return CNF

"""
    Get symbols from clauses. Use a set to record unique symbols.
    @:param clauses: list of clauses, which are lists of literals
    @:return a list of symbols, each of which is a coordinate
"""
def getSymbols(clauses):
    res_symbols = []
    unique_symbols = set()
    for clause in clauses:
        for item in clause:
            unique_symbols.add((item[0], item[1]))
    for item in unique_symbols:
        res_symbols.append([item[0], item[1]])
    return res_symbols

"""
    Helper method of DPLL.
    Return 'T' if the clause is true when value is assigned as model.
    Return 'F' if the clause is false when value is assigned as model.
    Return 'NA' if the condition is not applicable to be true or false when value is assigned as model.
"""
def clauseCondition(clause, model):
    NA = False
    for item in clause:
        if (item[0], item[1]) in model:
            if model[(item[0], item[1])] == item[2]:
                return 'T'
        else:
            NA = True
    if NA:
        return 'NA'
    else:
        return 'F'

"""
    Unit tester of clauseCondition.
"""
def clauseConditionTester():
    clauses1 = [[1, 1, 1], [1, 2, 0]]
    model1 = dict()
    model1[(1, 1)] = 1
    model1[(1, 2)] = 0
    print clauseCondition(clauses1, model1)
    model2 = dict()
    model2[(1, 1)] = 0
    model2[(1, 2)] = 1
    print clauseCondition(clauses1, model2)
    model3 = dict()
    print clauseCondition(clauses1, model3)

"""
    Helper method of DPLL.
    @:param symbols: list of coordinates (first two terms of literals)
    @:param clauses: list of list of literals
    @:param model: a dict whose key is coordinates and value is 1/0
    @:return P, value: list of symbol and corresponding values
"""
def findPureSymbol(symbols, clauses, model):
    if len(symbols) == 0:
        return [], []
    pure = dict()
    inpure = set()
    for clause in clauses:
        # scan clause to determine if it's true
        waiveClause = False
        for item in clause:
            if (item[0], item[1]) in model and model[(item[0], item[1])] == item[2]:
                waiveClause = True
                break
        if waiveClause:
            continue
        # if it's not true, find if it's in inpure and pure
        for item in clause:
            key = (item[0], item[1])
            # do not need any operation
            if key in inpure:
                continue
            if key in pure:
                if pure[key] == item[2]:
                    continue
                # conflict
                else:
                    del pure[key]
                    inpure.add(key)
            # key not in pure
            else:
                pure[key] = item[2]
    P = []
    value = []
    for key, val in pure.iteritems():
        if key in symbols:
            P.append(key)
            value.append(val)
    return P, value

"""
   Unit tester of findPureSymbol method.
"""
def findPureSymbolTester():
    symbols = [[1, 1], [1, 2], [2, 1], [3, 2], [4, 3]]
    clauses = [[[1, 1, 0], [1, 2, 1]], [[2, 1, 1], [3, 2, 0], [1, 2, 0]], [[4, 3, 0], [2, 1, 0]], [[1, 1, 0], [3, 2, 0]]]
    model = dict()
    P1, value1 = findPureSymbol(symbols, clauses, model)
    print 'findPureSymbolTester'
    print 'example #1'
    for i in xrange(len(P1)):
        print str(P1[i]) + ' -> ' + str(value1[i])
    model[(1, 1)] = 0
    P2, value2 = findPureSymbol(symbols, clauses, model)
    print 'example #2'
    for i in xrange(len(P2)):
        print str(P2[i]) + ' -> ' + str(value2[i])

"""
    Helper method of DPLL.
    Remove symbols, which are listed in targets, from symbols.
    E.g. symbols = [[1, 2], [7, 9], [6, 3]] and targets = [[7, 9], [1, 2]]
    then the returned result should be [[6,3]]
    @:param symbols, targets: lists of symbols (coordinates)
    @:return: a new list of symbols
"""
def removeSymbols(symbols, targets):
    if len(targets) == 0:
        return symbols
    hashset = set()
    for item in symbols:
        hashset.add((item[0], item[1]))
    for item in targets:
        hashset.discard((item[0], item[1]))
    result = []
    for item in hashset:
        result.append([item[0], item[1]])
    return result

"""
    Unit tester of removeSymbols method.
"""
def removeSymbolsTester():
    symbols = [[1, 2], [7, 9], [6, 3]]
    targets = [[7, 9], [1, 2]]
    print removeSymbols(symbols, targets)
    print removeSymbols(symbols, [])
    print removeSymbols([], [])
    print removeSymbols([], [[1, 2]])

"""
    Helper method of DPLL.
    @:param model: dict of value assignments.
    @:param symbols: list of symbols to be updated.
    @:param values: list of values corresponding to symbols.
    @:return a new dict updated with symbol and value pairs.
    Assumption: len(symbols) == len(values)
"""
def updateModel(model, symbols, values):
    if len(values) == 0:
        return model
    newModel = dict()
    for key, value in model.iteritems():
        newModel[key] = value
    for i in xrange(len(values)):
        key = (symbols[i][0], symbols[i][1])
        if key not in newModel:
            newModel[key] = values[i]
    return newModel

"""
    Unit tester of updateModel method.
"""
def updateModelTester():
    model = dict()
    print 'initial model'
    for key, value in model.iteritems():
        print key, value
    symbols1 = [[1, 2], [2, 3]]
    values1 = [1, 0]
    newmodel1 = updateModel(model, symbols1, values1)
    print 'updated model1'
    for key, value in newmodel1.iteritems():
        print key, value
    symbols2 = [[3, 4], [8, 7]]
    values2 = [0, 1]
    newmodel2 = updateModel(newmodel1, symbols2, values2)
    print 'updated model2'
    for key, value in newmodel2.iteritems():
        print key, value

"""
    Helper method of DPLL.
    @:param clauses: list of clauses, each of which is a list of literals
    @:param model: dict with coordinates as key and 1/0 (pos/neg) as value
"""
def findUnitClause(clauses, model):
    res_P = []
    res_value = []
    newModel = dict()
    for key, value in model.iteritems():
        newModel[key] = value
    while True:
        localP = []
        localVal = []
        for clause in clauses:
            unassigned = []
            multiple = False
            alwaystrue = False
            for item in clause:
                key = (item[0], item[1])
                # already a negative in clause
                if key in newModel:
                    if newModel[key] != item[2]:
                        continue
                    else:
                        alwaystrue = True
                        break
                # no other unit symbol for unit clause yet
                elif len(unassigned) == 0:
                    unassigned.append(item)
                # >1 non-negatives, so this is not unit clause
                else:
                    multiple = True
                    break
            if multiple or alwaystrue:
                continue
            elif len(unassigned) == 1:
                localP.append([unassigned[0][0], unassigned[0][1]])
                localVal.append(unassigned[0][2])
        if len(localVal) == 0:
            break
        newModel = updateModel(newModel, localP, localVal)
        for i in xrange(len(localVal)):
            res_P.append(localP[i])
            res_value.append(localVal[i])
    return res_P, res_value

"""
    Unit tester of findUnitClause method.
"""
def findUnitClauseTester():
    print 'Unit Clause finder'
    print 'Example #1'
    clauses1 = [[[1, 1, 1], [1, 2, 0]], [[1, 2, 0], [1, 3, 0]], [[1, 3, 1], [1, 1, 1]]]
    model1 = dict()
    model1[(1, 2)] = 1
    P1, value1 = findUnitClause(clauses1, model1)
    for i in xrange(len(value1)):
        print str(P1[i]) + ' -> ' + str(value1[i])
    print 'Example #2'
    clauses2 = clauses1[1:]
    P2, value2 = findUnitClause(clauses2, model1)
    for i in xrange(len(value2)):
        print str(P2[i]) + ' -> ' + str(value2[i])

"""
    Helper method of DPLL.
    @:param model: solution to value assignments
"""
def saveSolution(model):
    global solutionModel
    solutionModel = dict()
    for key, value in model.iteritems():
        if value == 1:
            solutionModel[key[0]] = key[1]

"""
    DPLL method. Helper method of DPLL-Satisfiable.
    @:param clauses: a list of clauses, each of which is a list of literals
    @:param symbols: a list of symbols, each of which is a coordinate
    @:param model: a dict, whose key is coordinates, value is true(1) or false(0)
    return the satisfiability of clauses
"""
def DPLL(clauses, symbols, model):
    allTrue = True
    for clause in clauses:
        a = clauseCondition(clause, model)
        if a == 'F':
            allTrue = False
            return False
        elif a == 'NA':
            allTrue = False
            break
    if allTrue:
        saveSolution(model)
        return True
    P_pure, value_pure = findPureSymbol(symbols, clauses, model)
    if len(P_pure) != 0:
        return DPLL(clauses, removeSymbols(symbols, P_pure), updateModel(model, P_pure, value_pure))
    P_unit, value_unit = findUnitClause(clauses, model)
    if len(P_unit) != 0:
        return DPLL(clauses, removeSymbols(symbols, P_unit), updateModel(model, P_unit, value_unit))
    P = [symbols[0]]
    rest = symbols[1:]
    return DPLL(clauses, rest, updateModel(model, P, [1])) or DPLL(clauses, rest, updateModel(model, P, [0]))

"""
    Main method starts here:
"""
debugMode = False
inputfilepath = "input.txt"
outputfilepath = "output.txt"

with open("input.txt", "r") as f:
    for lineNum, line in enumerate(f):
        if lineNum == 0:
            guestNum = int(line.split()[0])
            tableNum = int(line.split()[1])
            R = []
        else:
            guest1 = int(line.split()[0])
            guest2 = int(line.split()[1])
            relation = line.split()[2]
            R.append([guest1, guest2, relation])

if debugMode:
    print "Guest number: " + str(guestNum)
    print "Table number: " + str(tableNum)

    for line in R:
        print line

clauses = getCNF(guestNum, tableNum, R)
symbols = getSymbols(clauses)
model = dict()
satisfiable = DPLL(clauses, symbols, model)

if debugMode:
    print 'satisfiable? ' + str(satisfiable)
    for key, value in solutionModel.iteritems():
        print str(key) + ' -> ' + str(value)

with open(outputfilepath, 'w') as outputf:
    if satisfiable:
        outputf.write("yes\n")
        for key, value in solutionModel.iteritems():
            outputf.write(str(key) + " " + str(value) + "\n")
    else:
        outputf.write("no")

if debugMode:
    clauseConditionTester()
    findPureSymbolTester()
    removeSymbolsTester()
    updateModelTester()
    findUnitClauseTester()