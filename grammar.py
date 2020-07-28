import string

class Grammar:

    term = string.ascii_lowercase
    var = string.ascii_uppercase
    vocab = set()
    rules = {}      # V: ['aBcD', 'ab']

    def getNewVar(self):
        for v in self.var:
            if v not in self.vocab:
                self.vocab.add(v)
                return v
        for i in range(1, 100000):
            for v in self.var:
                vi = v + str(i)
                if vi not in self.vocab:
                    self.vocab.add(vi)
                    return vi

    def tokenize(self, s):
        tokens = []
        temp = ''
        for i in range(len(s)):
            c = s[i]
            if i == len(s) - 1:
                if c.isdigit():
                    temp += c
                    tokens.append(temp)
                    temp = ''
                else:
                    if temp != '':
                        tokens.append(temp)
                    tokens.append(c)
                return tokens
            if c.isdigit():
                temp += c
            else:
                if temp != '':
                    tokens.append(temp)
                temp = ''
                if c in self.var:
                    temp += c
                else:
                    tokens.append(c)
        return tokens

    def removeLambda(self):
        nullables = set()
        for f, t in self.rules.items():
            for r in t:
                if r == '_':
                    nullables.add(f)
        existsNewNull = False
        while True:
            for f, t in self.rules.items():
                for r in t:
                    nullTest = r
                    for n in nullables:
                        if n in nullTest:
                            nullTest = nullTest.replace(n, '')
                    if nullTest == '' and f not in nullables:
                        nullables.add(f)
                        existsNewNull = True
            if not existsNewNull:
                break
            existsNewNull = False
        for t in self.rules.values():
            if '_' in t:
                t.remove('_')
        for f, t in self.rules.items():
            tp = t
            for r in t:
                nullInR = []
                for i in range(len(r)):
                    if r[i] in nullables:
                        nullInR.append(i)
                nullTableList = []
                comb = 2**len(nullInR) - 1
                combMask = 1
                while comb >= 0:
                    nullTable = {}
                    for i in range(len(nullInR)):
                        nullState = 1 if comb & combMask != 0 else 0
                        nullTable[nullInR[i]] = nullState
                        combMask <<= 1
                    nullTableList.append(nullTable)
                    comb -= 1
                    combMask = 1
                newRules = []
                for nt in nullTableList:
                    rp = ''
                    for i in range(len(r)):
                        if i in nullInR:
                            rp += r[i] if nt[i] == 1 else ''
                        else:
                            rp += r[i]
                    if rp != '':
                        newRules.append(rp)
                tp = list(set(tp + newRules))
            self.rules[f] = tp.copy()

    def removeUnit(self):
        hasUnit = False
        while True:
            for f, t in self.rules.items():
                newRules = []
                for r in t:
                    if len(r) == 1 and r in self.var:
                        hasUnit = True
                        if r in self.rules:
                            newRules = list(set(newRules + self.rules[r]))
                    else:
                        newRules.append(r)
                if f in newRules:
                    newRules.remove(f)
                self.rules[f] = newRules.copy()
            if not hasUnit:
                break
            hasUnit = False

    def toCNF(self):

        # Tokenize RHS
        for f, t in self.rules.items():
            newRules = []
            for r in t:
                newRules.append(self.tokenize(r))
            self.rules[f] = newRules

        # S on RHS
        newStart = self.getNewVar()
        self.rules[newStart] = self.rules.pop('S')
        for t in self.rules.values():
            for r in t:
                for i in range(len(r)):
                    if r[i] == 'S':
                        r[i] = newStart
        self.rules['S'] = self.rules[newStart].copy()

        # Variablize terminals
        termVars = {}    # term : var
        for f, t in self.rules.items():
            newRules = []
            for r in t:
                if len(r) == 1 and r[0] in self.term:
                    newRules.append([r[0]])
                    continue
                newR = []
                for symbol in r:
                    if symbol in self.term:
                        if symbol not in termVars:
                            termVars[symbol] = self.getNewVar()
                        newR.append(termVars[symbol])
                    else:
                        newR.append(symbol)
                newRules.append(newR)
            self.rules[f] = newRules.copy()
        varTerms = {}    # var : term
        for t, v in termVars.items():
            varTerms[v] = [[t]]
        self.rules = {**self.rules, **varTerms}

        # Shorten
        hasLongRule = False
        while True:
            catVar = {}
            for f, t in self.rules.items():
                newRules = []
                for r in t:
                    rp = r.copy()
                    if len(rp) > 2:
                        hasLongRule = True
                        newVar = self.getNewVar()
                        catVar[newVar] = [rp[1:]]
                        rp = [r[0], newVar]
                    newRules.append(rp)
                self.rules[f] = newRules.copy()
            self.rules = {**self.rules, **catVar}
            if not hasLongRule:
                break
            hasLongRule = False

        # Unify tokens
        for f, t in self.rules.items():
            newRules = []
            for r in t:
                newR = ''
                for symbol in r:
                    newR += symbol
                newRules.append(newR)
            self.rules[f] = newRules

    def readRules(self):
        n = int(input())
        for _ in range(n):
            f, t = input().split()
            for s in f, t:
                for c in s:
                    if c in self.var:
                        self.vocab.add(c)
            self.rules.setdefault(f, []).append(t)

    def printRules(self):
        lines = len(sum((self.rules.values()), []))
        print(lines)
        for f, t in self.rules.items():
            for r in t:
                print(f + ' ' + r)
