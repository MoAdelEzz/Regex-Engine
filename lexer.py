class Lexer:
    iter: int
    tokenized_regex: list[str]
    groups: dict
    matchers: dict
    ranges: dict
    quantifiers: dict
    def __init__(self, regex: str):
        self.regex = regex
        self.iter = 0
        self.groups = {}
        self.matchers = {}
        self.ranges = {}
        self.quantifiers = {}
        self.tokenized_regex = []
        self.validate()
        self.tokenize()

    def reset(self):
        self.iter = 0

    def validate(self):
        group_stack = []
        matcher_stack = []
        for idx, char in enumerate(self.regex):
            if len(matcher_stack) > 0 and char not in [']', '-']:
                continue

            match char:
                case '(':
                    group_stack.append(idx); continue
                case '[':
                    matcher_stack.append(idx); continue
                case ')':
                    if len(group_stack) == 0:
                        raise Exception(f"Invalid regex at position {idx}, no opening parenthesis for closing parenthesis")
                    group_stack.pop(); continue
                case ']':
                    if len(matcher_stack) == 0:
                        raise Exception(f"Invalid regex at position {idx}, no opening bracket for closing bracket")
                    matcher_stack.pop(); continue
                case '*' | '+' | '?':
                    if idx == 0 or self.regex[idx-1] in ['|', '*', '+', '?', '-', '(', '[']: 
                        raise Exception(f"Invalid regex at position {idx}, multiple quantifiers")
                    continue
                case '-' | '|':
                    if idx == 0 or self.regex[idx-1] in ['|', '*', '+', '?', '-', '(', '[']: 
                        raise Exception(f"Invalid regex at position {idx}")
                    if idx == len(self.regex) - 1 or self.regex[idx+1] in ['|', '*', '+', '?', '-', ')', ']']:
                        raise Exception(f"Invalid regex at position {idx}")
        
        if len(group_stack) != 0 or len(matcher_stack) != 0:
            raise Exception(f"No closing parenthesis or bracket at the end of the regex")
            
        return True
    
    def tokenize_ranges(self):
        for key, tokens in self.matchers.items():
            tokenized_regex = []
            skip = False
            for idx, token in enumerate(self.matchers[key]):
                if skip: 
                    skip = False
                    continue

                elif token == "-":
                    self.ranges[len(self.ranges)] = [ tokenized_regex[-1], tokens[idx+1] ]
                    tokenized_regex[-1] = (f"RANGE-{len(self.ranges) - 1}")
                    skip = True

                else:
                    tokenized_regex.append(token)
            self.matchers[key] = tokenized_regex
        
    def two_operands_tokenizer(self, tokens: list[str]):
        tokenized_regex = []
        skip = 0
        for idx, token in enumerate(tokens):
            if skip: 
                skip -= 1
                continue

            if token == "|":
                try:
                    next_or = idx + 1 + tokens[idx + 1 : ].index("|")
                except ValueError:
                    next_or = len(tokens)
                
                if len(tokenized_regex) > 1:
                    self.groups[ len(self.groups) ] = tokenized_regex.copy()
                    tokenized_regex[:] = [f"GROUP-{len(self.groups) - 1}"]

                next_token = tokens[idx+1]
                if next_or > 1:
                    self.groups[len(self.groups)] = tokens[idx+1 : next_or]
                    next_token = f"GROUP-{len(self.groups) - 1}"

                self.matchers[len(self.matchers)] = [tokenized_regex[-1], next_token]
                tokenized_regex[:] = [f"MATCHER-{len(self.matchers) - 1}"]
                skip = next_or - idx - 1

            else:
                tokenized_regex.append(token)

        return tokenized_regex
    
    def make_matcher_bad(self, tokens: str):
        prev = tokens[0]
        for token in tokens[1:]:
            self.matchers[len(self.matchers)] = [prev, token]
            prev = f"MATCHER-{len(self.matchers) - 1}"
        return prev

    
    def tokenize(self, regex: str = None):
        if regex is None:
            regex = self.regex

        group_stack = []
        matcher_stack = []
        inter_regex = []

        for char in regex:
            if len(matcher_stack) > 0 and char not in [']', '-']:
                inter_regex.append(char)
                continue

            match char:
                case '(':
                    group_stack.append(len(inter_regex)); continue
                
                case '[':
                    matcher_stack.append(len(inter_regex)); continue
                
                case ')':
                    inter_regex_start = group_stack[-1]
                    self.groups[ len(self.groups) ] = inter_regex[ inter_regex_start : ]
                    inter_regex[ inter_regex_start : ] = [f"GROUP-{len(self.groups) - 1}"]
                    group_stack.pop(); 
                    continue
                
                case ']':
                    inter_regex_start = matcher_stack[-1]
                    self.matchers[ len(self.matchers) ] = inter_regex[ inter_regex_start : ]
                    inter_regex[ inter_regex_start : ] = [f"MATCHER-{len(self.matchers) - 1}"]
                    matcher_stack.pop()
                    continue
                
                case '*' | '+' | '?':
                    if len(matcher_stack) > 0:
                        inter_regex.append(char)
                        continue
                    
                    target = inter_regex[-1]
                    inter_regex[-1] = f"QUANTIFIER-{len(self.quantifiers)}"
                    self.quantifiers[len(self.quantifiers)] = (char, target)
                
                case _:
                    inter_regex.append(char)
        
        inter_regex = self.two_operands_tokenizer(inter_regex)

        self.tokenize_ranges()

        for key in list(self.quantifiers.keys()):
            self.quantifiers[key] = self.two_operands_tokenizer(self.quantifiers[key])

        for key in list(self.groups.keys()):
            self.groups[key] = self.two_operands_tokenizer(self.groups[key])

        for key in list(self.ranges.keys()):
            self.ranges[key] = self.two_operands_tokenizer(self.ranges[key])

        for matcher in list(self.matchers.keys()):
            self.matchers[matcher] = [self.make_matcher_bad(self.matchers[matcher])]

        self.tokenized_regex = inter_regex
        return self.tokenized_regex
    
