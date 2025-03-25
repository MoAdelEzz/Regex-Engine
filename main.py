from helper import *
from testcases import *

from lexer import Lexer
from parser import Parser
from nfa import NFA
from dfa import DFA
from minimized_dfa import MinDfa


regex, accept, reject = TEST_CASES[0]

lexer = Lexer(regex)
parser = Parser(lexer)

nfa = NFA(parser.nodes)
nfaStateMachine = nfa.ToJson()
DrawSM(regex, nfaStateMachine, title="NFA")
WriteJson(nfaStateMachine, title="NFA")

dfa = DFA(nfa.ToJson())
dfaStateMachine = dfa.ToJson()
DrawSM(regex, dfaStateMachine, title="DFA")
WriteJson(dfaStateMachine, title="DFA")

min_dfa = MinDfa(dfa.ToJson())
MinDfaStateMachine = min_dfa.ToJson()
DrawSM(regex, MinDfaStateMachine, title="Minimized DFA")
WriteJson(MinDfaStateMachine, title="MinDFA")



print(Test(dfaStateMachine, accept))
print(Test(dfaStateMachine, reject))