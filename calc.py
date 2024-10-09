import asyncio
from math import factorial
from decimal import Decimal

class BaseCalc:
    # Удаление нулей в конце числа после запятой (наследие с C++)
    @staticmethod
    async def removing_zeros(expression: str) -> str:
        if '.' in expression:
            while expression[-1] == '0': expression = expression[:-1]
            if expression and expression[-1] == '.': expression = expression[:-1]
        return expression if expression else '0'

class CalculateMain:
    # Методподсчёта скобок
    async def _counting_parentheses(self, expression: str) -> list[int]:
        return [expression.count('('), expression.count(')')]
    async def _find_nth_occurrence(self, string: str, substring: str, n: int) -> int:
        start = 0
        for _ in range(n):
            start = string.find(substring, start)
            if start == -1:
                return -1  # Если подстрока не найдена
            start += len(substring)
        return start - len(substring)
    # Метод для поиска приоритетных скобок
    async def _searching_for_priority_brackets(self, expression: str, number_of_bracket: int) -> list[int]:
        return [(number_last_open_brackets := await self._find_nth_occurrence(expression, '(', number_of_bracket)), expression.find(')', number_last_open_brackets)]
    # Метод проверки на равность двух чисел
    async def _equality_of_two_numbers(self, counting_parentheses: list[int]) -> bool:
        return counting_parentheses[0] == counting_parentheses[1]
    # Проверка наличия операции вычитания
    async def _has_operations(self, expression: str) -> bool:
        return any(c in '+-*/' for c in expression)
    # Разбиение строки на отдельные элементы (числа и операторы)
    async def _tokenize(self, expression: str) -> list[str]:
        tokens: list[str] = list()
        token: str = ""
        minus: bool = True
        
        for c in expression:
            if c.isdigit() or c == '.' or (minus and c == '-'):
                token += c
                minus = False
            else:
                minus = True
                if token:
                    tokens.append(token)
                    token = ""
                tokens.append(c)  # Оператор
        
        if token:
            tokens.append(token)  # Последнее число в выражении
        
        return tokens
    async def _calculate_expression_priority(self, tokens: list[str]) -> list[str]:
        if not ('%' in tokens or '!' in tokens): return tokens
        t: int
        while '%' in tokens:
            t = tokens.index('%')
            print(tokens)
            tokens.pop(t)
            tokens[t-1] = str(Decimal(tokens[t-1])/Decimal(100))
        while '!' in tokens:
            t = tokens.index('!')
            tokens.pop(t)
            tokens[t-1] = factorial(int(tokens[t-1]))
        return tokens
            
    async def _calculate_expression_base(self, tokens: list[str]) -> str:
        print(tokens)
        result: Decimal = Decimal(tokens[0])
        last_operator: str = '+'
        token: str
        num: Decimal
        for i in range(1, len(tokens)):
            token = tokens[i]
            if token in {"+", "-", ":","*", "/", "^", "×", "−"}:
                last_operator = token
            else:
                num = Decimal(token)
                if i > 1 and tokens[i - 2] == "-":
                    num *= -1
                # Выполнение действий
                match last_operator:
                    case '+': result += num
                    case '-' | '−': result -= num
                    case '*' | '×' : result *= num
                    case '/' | ':' :
                        if num != 0:
                            result /= num
                        else:
                            raise ZeroDivisionError("Division by zero")
                    case '^' : result **= num
        
        return str(result)
    # Основная функция подсчёта
    async def calc_main(self, *, expression: str) -> str:
        expression = expression.replace(" ", "")
        try:
            if not (await self._equality_of_two_numbers(await self._counting_parentheses(expression))):
                raise UnequalNumberOfParenthesesException()
            
            expression_1 = expression
            while (await self._counting_parentheses(expression_1))[0] != 0:
                priority_brackets = await self._searching_for_priority_brackets(
                    expression_1, 
                    (await self._counting_parentheses(expression_1))[0]
                )
                inner_expression = expression_1[priority_brackets[0] + 1:priority_brackets[1]]
                expression_1 = (
                    expression_1[:priority_brackets[0]] +
                    (await self._calculate_expression_base(await self._calculate_expression_priority(await self._tokenize(inner_expression)))) +
                    expression_1[priority_brackets[1] + 1:]
                )
            return await BaseCalc.removing_zeros(str(await self._calculate_expression_base(await self._calculate_expression_priority(await self._tokenize(expression_1)))))
            
        except Exception as e:
            print(e)
            return expression
"""
class Percent:
    self._operators_4: str = "+=/*"
    self._operators_2: str = "/*"
    async def _computeResult(priority_operator: str, kl: str) -> str:
        result: str
        if self._operators_2:
            result = str(float(kl)/100)
        else:
            kl_1: str 
"""
async def main() -> None:
    CalculateMain_v = CalculateMain()
    while True:
        print(await CalculateMain_v.calc_main(expression = str(input("Input expression :"))))
asyncio.run(main())

