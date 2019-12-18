import sys
from time import time

# basic backtracking algorithm without DPLL heuristics applied
def backtrack(f):
    # Try valuing the next unvalued variable.
    for v in f.vars:
        # if value has not yet been assigned
        if v.value == None:
            for value in [True, False]:   # 2 possible values
                v.value = value
                if not f.unsat():
                    r = backtrack(f)     # recurrence: T(n) = 2T(n-1) + p, 
                                          # where p is some first-degree polynomial
                                          # p = O(c * l), where c is the number of clauses
                                          # and l is the number of literals given in the input
                    if r != None:
                        return r
                # else backtrack
            v.value = None
            return None

    # All variables have been valued. Check to see if it's a solution
    if f.sat():
        return f.vars
    return None

# Simplified Davis–Putnam–Logemann–Loveland (DPLL) algorithm
# includes unit propogation but no pure literal elimination
def dpll(f):
    # unit propogation
    unit_clauses = []
    for c in f.clauses:
        # look for unit clauses
        if len(c) == 1:
            lit = c.lits[0]
            curr_val = f.vars[int(lit.var.name) - 1].value
            if curr_val and (curr_val != lit.sign):
                # cannot be satisfied
                return None
            # variable must be this value in order for f to be sat
            # this will reduce the number of recursive calls needed below
            f.vars[int(lit.var.name) - 1].value = lit.sign
            unit_clauses.append(c)
            
    # remove unecessary unit clauses to improve speedup
    f.clauses = [x for x in f.clauses if x not in unit_clauses]
    
    # call backtracking algorithm with improvements
    return backtrack(f)

#################################################################

class Var(object):
    def __init__(self, name, value=None):
        self.name = name
        self.value = value

    def __str__(self):
        return str(self.name)

class Lit(object):
    def __init__(self, var, sign):
        self.var = var
        self.sign = sign

    # Returns True iff the literal evaluates positively (and is not None)
    def sat(self):
        return self.var.value == self.sign

    # Returns True iff the literal evaluates negatively (or is None)
    def unsat(self):
        if self.var.value == None or self.sat():
            return False
        return True

    def __str__(self):
        name = str(self.var)
        if self.sign:
            return name
        return "-" + name

class Clause(object):
    def __init__(self, lits):
        self.lits = lits

    # Returns True if *some* literal in the clause evaluates positively
    # (T v F v F ...) == T
    def sat(self):
        for l in self.lits:
            if l.sat():
                return True
        return False

    # Returns True if *every* literal in the clause evaluates
    # (F v F v F) == F
    def unsat(self):
        for l in self.lits:
            if not l.unsat():
                return False
        return True

    def __str__(self):
        return " ".join([str(l) for l in self.lits]) + " 0"
    
    def __len__(self):
        return len(self.lits)

class Formula(object):
    def __init__(self, vars, clauses):
        self.vars = vars
        self.clauses = clauses

    # Returns True iff *every* clause in the formula is sat
    def sat(self):
        for c in self.clauses:
            if not c.sat():
                return False
        return True

    # Returns True iff *some* clause in the formula is unsat
    def unsat(self):
        for c in self.clauses:
            if c.unsat():
                return True
        return False
        
    def __str__(self):
        comment = "c Formula in DIMACS format\n"
        header = "p cnf {} {}\n".format(len(self.vars), len(self.clauses))
        clauses = "\n".join([str(c) for c in self.clauses])
        return comment + header + clauses

    
# Read a CNF formula from the given file in DIMACS format
def read_formula(filename):
    with open(filename, "r") as f:
        # Strip leading comments.
        while True:
            header = next(f).strip()
            if header[0] != 'c':
                break

        # Parse header and create variables.
        hfields = header.split()
        assert len(hfields) == 4
        assert hfields[0] == 'p'
        assert hfields[1] == 'cnf'
        nvars = int(hfields[2])
        nclauses = int(hfields[3])
        vars = [Var(name + 1) for name in range(nvars)]

        clauses = []
        for row in f:
            cvars = row.split()
            ncvars = len(cvars)
            assert int(cvars[ncvars - 1]) == 0
            clause = []
            for i in range(ncvars - 1):
                cvar = int(cvars[i])
                assert cvar != 0
                sign = cvar > 0
                cvar = abs(cvar)
                clause.append(Lit(vars[cvar - 1], sign))
            clauses.append(Clause(clause))

        return Formula(vars, clauses)

    
# Print a solution in DIMACS format
def print_soln(soln):
    if soln == None:
        print("s UNSATISFIABLE")
    else:
        print("s SATISFIABLE")
        asgs = ["v"]
        for v in soln:
            if v.value == True:
                asgs.append(str(v))
            elif v.value == False:
                asgs.append("-" + str(v))
        asgs.append("0")
        print(" ".join(asgs))

#################################################################

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: yass <dimacs-file>")

    f = read_formula(sys.argv[1])

    ts = time()
    r1 = backtrack(f)
    t1 = time() - ts

    ts = time()
    r2 = dpll(f)
    t2 = time() - ts

    print_soln(r1)
    print_soln(r2)

    print()
    print("Backtrack implementation time:\t",t1)
    print("DPLL implementation time:\t",t2)
