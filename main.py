from drawer import *
from lexer import Lexer
from parser import Parser
from nfa import NFA
from dfa import DFA
from minimized_dfa import MinDfa
from helper import *

# PASSED

regex = "(a*)*"
regex = "(a*b)(b?a+)"
regex = "(a*b*)([a-b]*)"
regex = "(a+a+)+b"
regex = "(a|b)*a[ab]?"
regex = "[a-c]*"
regex = "[A-Ea-c]+1|2[0-9]*K?[ABC](ABC)"
regex = "[a-f0-9]32"

regex = "[a-fA-C]"
regex = "[abc](d|e|f)"
regex = "[bc]*(cd)+"
regex = "a*b*[a-z](c?)"
regex = "a*|b*"
regex = "a*b*ca"
regex = "a+|b+"
regex = "a+b"
regex = "a+b*"
regex = "a+b*a"
regex = "ab(b|c)*d+"
regex = "employ(er|ee|ment|ing|able)"

# regex = "ab*"
# regex = "a|bc"
# regex = "[ab]"
# regex = "b*c+d"
# regex = "ab*c+de?(f|g|h)|mr|n|[pq]"
# regex = "a+"
# regex = "(a*b)(b*a+)"
# regex = "(a+*a+*)+*b"
# regex = "abcd"
# regex = "[[a-z]A-Z]*"
# regex = "[A-Ea-c]+1*2[0-9]*K*[ABC](ABC)"

# VAR CHECK

# PENDING
# regex = "[a-f0-9]32"
# regex = "[a-fA-C]"
# regex = "[abc](d*e*f)"
# regex = "[bc]*(cd)+"
# regex = "a*b+ [a-z](c*)"
# regex = "a*b*"
# regex = "a*b*ca"
# regex = "a+*b+"
# regex = "a+b"
# regex = "a+b*"
# regex = "a+b*a"
# regex = "abcd"


# regex = "a+"
# regex = "Aym(O|o)na?"
# regex = "a(b|cd(e|f))d"


lexer = Lexer(regex)
parser = Parser(lexer)
nfa = NFA(parser.nodes)
state_machine = nfa.ToJson()
DrawSM(regex, state_machine, title="NFA")

dfa = DFA(nfa.ToJson())
state_machine = dfa.ToJson()
DrawSM(regex, state_machine, title="DFA")

min_dfa = MinDfa(dfa.ToJson())
min_dfa.Minimize()
state_machine = min_dfa.merge()
DrawSM(regex, state_machine, title="Minimized DFA")
