class LR0Parser:
    def __init__(self, grammar):
        self.grammar = grammar
        self.states = []
        self.transitions = {}
        self.special_rule = None
        self.non_terminals = set()
        self.build_automaton()

    def build_automaton(self):
        # Создаем новый нетерминал
        n = 0
        new_start_symbol = self.grammar[0][0] + str(n)

        # Проверяем, что новый нетерминал не существует в грамматике
        while any(new_start_symbol == rule[0] for rule in self.grammar):
            n += 1
            new_start_symbol = new_start_symbol[:1] + str(n)


        # Добавляем новое правило в грамматику
        new_rule = (new_start_symbol, (self.grammar[0][0]))
        self.grammar.append(new_rule)
        self.special_rule = new_rule

        # Сохраняем все уникальные нетерминалы
        self.non_terminals = {rule[0] for rule in self.grammar}

        # Инициализация начального состояния
        start_state = self.closure({(new_rule, 0)})
        self.states.append(start_state)

        # Построение таблицы переходов
        for state in self.states:
            for symbol in self.get_symbols(state):
                next_state = self.goto(state, symbol)
                if next_state and next_state not in self.states:
                    self.states.append(next_state)
                self.transitions[(frozenset(state), symbol)] = next_state

    def closure(self, items):
        closure_set = set(items)
        while True:
            new_items = set(closure_set)
            for item in closure_set:
                production, dot_position = item
                #print(dot_position, len(production[1]), production)
                if dot_position < len(production[1]):
                    next_symbol = production[1][dot_position]
                    if self.is_non_terminal(next_symbol):  # Проверка, является ли следующий символ нетерминалом
                        for prod in self.grammar:
                            if prod[0] == next_symbol:
                                new_items.add((prod, 0))
            if new_items == closure_set:
                break
            closure_set = new_items

        return closure_set

    def goto(self, state, symbol):
        goto_state = set()
        for item in state:
            production, dot_position = item
            if dot_position < len(production[1]) and production[1][dot_position] == symbol:
                goto_state.add((production, dot_position + 1))
        return self.closure(goto_state) if goto_state else None

    def get_symbols(self, state):
        symbols = set()
        for item in state:
            production, dot_position = item
            if dot_position < len(production[1]):
                symbols.add(production[1][dot_position])
        return symbols

    def is_non_terminal(self, symbol):
        # Проверка, является ли символ нетерминалом
        return symbol in self.non_terminals

    def parse(self, input_string):
        return self.parse_recursive([frozenset(self.states[0])], input_string + '$', 0)

    def parse_recursive(self, stack, input_string, index):
        state = stack[-1]
        current_symbol = input_string[index]
        if stack and stack[-1] == frozenset({(self.special_rule, 1)}):
            if current_symbol == '$':
                return True
            else:
                return False

        next_state = self.transitions.get((state, current_symbol))
        if next_state:
            original_stack = stack.copy()
            stack.append(frozenset(next_state))
            if self.parse_recursive(stack, input_string, index + 1):
                return True
            stack = original_stack

        # Проверка всех возможных редукций
        for item in state:
            if item[1] == len(item[0][1]):
                non_terminal = item[0][0]
                production = item[0]
                # Сохраняем текущее состояние стека
                original_stack = stack.copy()
                # Снимаем со стека количество состояний, равное длине правой части правила
                for symbol in production[1]:
                    stack.pop()
                if stack:
                    prev_state = stack[-1]
                    next_state = self.transitions.get((prev_state, non_terminal))
                    if next_state:
                        stack.append(frozenset(next_state))
                        if self.parse_recursive(stack, input_string, index):
                            return True
                        # Восстанавливаем состояние стека
                        stack = original_stack

        return False
# Приведение грамматики к удобному виду
def input_grammar(strings):
    non_terminals = set()
    for s in strings:
        non_terminal = s[:s.find('-')]
        non_terminals.add(non_terminal)
    grammar = []
    for s in strings:
        div = s.find('-')
        non_terminal = s[:div]
        div += 2
        rules = s[div:] + '|'
        div = 0
        rule = []
        while rules != "":
            if rules[div] == '|':
                grammar.append((non_terminal, tuple(rule)))
                rules = rules[div + 1:]
                div = 0
                rule = []
            elif rules[div].islower():
                rule.append(rules[div])
                div += 1
            else:
                symbol = rules[div]
                div += 1
                while (not (symbol in non_terminals)) or ((div < len(rules)) and (rules[div].isdigit())):
                    symbol = symbol + rules[div]
                    div += 1
                rule.append(symbol)
    return grammar
# Пример использования
'''
grammar = [
    ('S', ('a', 'S', 'b',)),
    ('S', ('c',)),
    ('S', ('A1',)),
    ('A1', ('a', 'A1',)),
    ('A1', ('A2',)),
    ('A2', ('c', 'A2',)),
    ('A2', ('b',))
]
'''
grammar1=["S->aSb|c|A1", "A1->aA1|A2", "A2->cA2|b"]
grammar=input_grammar(grammar1)
parser = LR0Parser(grammar)
input_string = "aaaaaacbb"
result = parser.parse(input_string)
print("Parse Result:", result)
