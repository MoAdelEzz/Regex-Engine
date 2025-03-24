from drawer import *
from lexer import Lexer
from parser import Parser
from nfa import NFA
from dfa import DFA
from minimized_dfa import MinDfa
import json


# PASSED

# regex = "ab*c+de?(f|g|h)|mr|n|[pq]"
# regex = "(a*)*"
regex = "(a*b*)([a-b]*)"
# regex = "(a|b)*a[ab]?"
# regex = "(a*b)(b*a+)"
# regex = "(a+*a+*)+*b"
# regex = "(a+a+)+b"
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

# regex = "ab*"

lexer = Lexer(regex)
parser = Parser(lexer)
nfa = NFA(parser.nodes)

dfa = DFA()
dfa.convert(nfa.to_json())
state_machine = dfa.to_json()

min_dfa = MinDfa(dfa.to_json())
min_dfa.minimize()
state_machine = min_dfa.merge()

# print(nfa.test("mohammedAdel123"))
draw_NFA(regex, state_machine)
