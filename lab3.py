
class LR0Parser:
    def __init__(self, grammar):
        self.grammar = grammar
        self.states = []
        self.transitions = {}
        self.special_rule = None
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
        new_rule = (new_start_symbol, self.grammar[0][0])
        self.grammar.append(new_rule)
        self.special_rule = new_rule

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
                if dot_position < len(production[1]):
                    next_symbol = production[1][dot_position]
                    if next_symbol.isupper():  # Проверка, является ли следующий символ нетерминалом
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

    def parse(self, input_string):
        return self.parse_recursive([frozenset(self.states[0])], input_string+'$', 0)

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
            stack.append(frozenset(next_state))
            original_stack = stack.copy()
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
                for _ in range(len(production[1])):
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


# Пример использования
grammar = [
    ('S', 'aSb'),
    ('S', 'A'),
    ('S', 'c'),
    ('A', 'aA'),
    ('A', 'cb')
]

parser = LR0Parser(grammar)
input_string = "aaaaaacbb"
result = parser.parse(input_string)
print("Parse Result:", result)
