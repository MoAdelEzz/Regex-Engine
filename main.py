from utils import *
from drawer import *
import json


# PASSED
# regex = "(a*)*"

# VAR CHECK
# regex = "(a*b*)([a-b]*)"

regex = "abcd"
# regex = "(a|b)*a[ab]?"

# PENDING
# regex = "(a*b)(b*a+)"
# regex = "(a+*a+*)+*b"
# regex = "(a+a+)+b"
# regex = "[a-c]*"
# regex = "[A-Ea-c]+1*2[0-9]*K*[ABC](ABC)"
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



root = Node.create_root_node()
root.parse(regex)
root.to_state_machine()

for key, value in states.items():
    print(key, value)

draw_NFA(states)
