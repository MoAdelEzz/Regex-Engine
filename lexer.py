class Lexer:
    iter: int
    def __init__(self, regex: str):
        self.regex = regex
        self.iter = 0
    
    def reset(self):
        self.iter = 0

    def validate(self):
        group_stack = []
        matcher_stack = []
        for idx, char in enumerate(self.regex):
            match char:
                case '(':
                    group_stack.append(); break
                case '[':
                    matcher_stack.append(); break
                case ')':
                    if len(group_stack) == 0:
                        raise Exception(f"Invalid regex at position {idx}, no opening parenthesis for closing parenthesis")
                    group_stack.pop(); break
                case ']':
                    if len(matcher_stack) == 0:
                        raise Exception(f"Invalid regex at position {idx}, no opening bracket for closing bracket")
                    matcher_stack.pop(); break
                case '|' | '*' | '+' | '?' | '-' as quantifier:
                    if idx == 0 or self.regex[idx-1] in quantifier: 
                        raise Exception(f"Invalid regex at position {idx}, multiple quantifiers")
                case '-' | '|' as two_operand_quantifiers:
                    if idx == len(self.regex) - 1 or self.regex[idx+1] in two_operand_quantifiers:
                        raise Exception(f"Invalid regex at position {idx}, no character before or after this quantifier")
                    break
        return True
    

    def tokenize(self):
        char = self.regex[self.iter]
        self.iter += 1
        matcher = {"(": ")", "[": "]"}
        node_type = {"(": "AND", "[": "OR"}

        if char in ["(", "["]:
            stack = [char]
            while len(stack) > 0:
                if self.regex[self.iter] in ["(", "["]:
                    stack.append(self.regex[self.iter])
                elif self.regex[self.iter] == matcher[stack[-1]]:
                    stack.pop()
                self.iter += 1

            return 
            
        return char