from __future__ import annotations

class Lexer:
    iter: int
    tokenizedRegex: list[str]
    groups      : dict[str, list[str]]
    matchers    : dict[str, list[str]]
    ranges      : dict[str, list[str]]
    quantifiers : dict[str, list[str]]

    def __init__(self: Lexer, regex: str):
        self.regex = regex
        self.iter = 0
        self.groups = {}
        self.matchers = {}
        self.ranges = {}
        self.quantifiers = {}
        self.tokenizedRegex = []
        self.Validate()
        self.tokenizedRegex = self.Tokenize(regex)

    def Validate(self: Lexer) -> None:
        groupStack = []
        matcherStack = []
        for idx, char in enumerate(self.regex):
            if len(matcherStack) > 0 and char not in [']', '-']:
                continue

            match char:
                case '(':
                    groupStack.append(idx)
                case '[':
                    matcherStack.append(idx)
                case ')':
                    if len(groupStack) == 0:
                        raise Exception(f"Invalid regex at position {idx}, no opening parenthesis for closing parenthesis")
                    groupStack.pop()
                case ']':
                    if len(matcherStack) == 0:
                        raise Exception(f"Invalid regex at position {idx}, no opening bracket for closing bracket")
                    matcherStack.pop()
                case '*' | '+' | '?':
                    if idx == 0 or self.regex[idx-1] in ['|', '*', '+', '?', '-', '(', '[']: 
                        raise Exception(f"Invalid regex at position {idx}, multiple quantifiers")
                case '-' | '|':
                    if idx == 0 or self.regex[idx-1] in ['|', '-', '(', '[']: 
                        raise Exception(f"Invalid regex at position {idx}, nothing before operator")
                    if idx == len(self.regex) - 1 or self.regex[idx+1] in ['|', '*', '+', '?', '-', ')', ']']:
                        raise Exception(f"Invalid regex at position {idx}, nothing after operator")
        
        if len(groupStack) != 0 or len(matcherStack) != 0:
            raise Exception(f"No closing parenthesis or bracket at the end of the regex")
                
    def TokenizeRanges(self: Lexer) -> None:
        for matcherKey, tokens in self.matchers.items():
            result = []
            dashPositions = [-2] + [ idx for idx, token in enumerate(tokens) if token == "-" ] + [len(tokens) + 1]
            for prev, curr in zip(dashPositions, dashPositions[1:]):
                result.extend(tokens[prev + 2 : curr - 1])
                if curr < len(tokens):
                    self.ranges[len(self.ranges)] = [ tokens[curr - 1], tokens[curr + 1] ]
                    result.append(f"RANGE-{len(self.ranges) - 1}")
            
            self.matchers[matcherKey] = result

    def SerializedOring(self: Lexer, tokens: list[str]) -> str:
        result = tokens[0]
        for token in tokens[1:]:
            self.matchers[len(self.matchers)] = [result, token]
            result = f"MATCHER-{len(self.matchers) - 1}"
        return result
    
    def TokenizePipeOperator(self: Lexer, tokens: list[str]) -> list[str]:
        pipePositions = [-1] + [ idx for idx, token in enumerate(tokens) if token == "|" ] + [len(tokens) + 1]
        
        if len(pipePositions) == 2:
            return tokens

        groupedTokens = []
        for prev, curr in zip(pipePositions, pipePositions[1:]):
            if curr - (prev + 1) == 1:
                groupedTokens.append(tokens[prev + 1])
            else:
                self.groups[len(self.groups)] = tokens[prev + 1 : curr]
                groupedTokens.append(f"GROUP-{len(self.groups) - 1}")
                
        return [ self.SerializedOring(groupedTokens) ]
    
    def Tokenize(self: Lexer, regex: str) -> list[str]:
        groupStack = []
        matcherStack = []
        interRegex = []

        for char in regex:
            if len(matcherStack) > 0 and char not in [']', '-']:
                interRegex.append(char)
                continue

            match char:
                case '(':
                    groupStack.append(len(interRegex)); continue
                
                case '[':
                    matcherStack.append(len(interRegex)); continue
                
                case ')':
                    inter_regex_start = groupStack[-1]
                    self.groups[ len(self.groups) ] = interRegex[ inter_regex_start : ]
                    interRegex[ inter_regex_start : ] = [f"GROUP-{len(self.groups) - 1}"]
                    groupStack.pop(); 
                    continue
                
                case ']':
                    inter_regex_start = matcherStack[-1]
                    self.matchers[ len(self.matchers) ] = interRegex[ inter_regex_start : ]
                    interRegex[ inter_regex_start : ] = [f"MATCHER-{len(self.matchers) - 1}"]
                    matcherStack.pop()
                    continue
                
                case '*' | '+' | '?':
                    if len(matcherStack) > 0:
                        interRegex.append(char)
                        continue
                    
                    target = interRegex[-1]
                    interRegex[-1] = f"QUANTIFIER-{len(self.quantifiers)}"
                    self.quantifiers[len(self.quantifiers)] = (char, target)
                
                case _:
                    interRegex.append(char)

        self.TokenizeRanges()
        interRegex = self.TokenizePipeOperator(interRegex)
        for collection in [self.quantifiers, self.groups, self.ranges]:
            for key in list(collection.keys()):
                collection[key] = self.TokenizePipeOperator(collection[key])

        return interRegex