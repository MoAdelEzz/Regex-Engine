from utils import *
from drawer import *
from lexer import Lexer
from parser import Parser
from nfa import NFA
from dfa import DFA
import json


# PASSED
# regex = "[a-zA-Z]"
# regex = "(a*)*"
# regex = "(a*b*)([a-b]*)"
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
regex = "[ab]+"
lexer = Lexer(regex)
parser = Parser(lexer)
nfa = NFA(parser.nodes)

dfa = DFA()
dfa.convert(nfa.to_json())
state_machine = dfa.to_json()

# print(nfa.test("mohammedAdel123"))

print(states)
draw_NFA(regex, state_machine)
