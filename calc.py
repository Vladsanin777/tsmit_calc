import gi
import random
import asyncio
from math import factorial
from decimal import Decimal

gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, Gdk


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
                if token in "%!":
                    minus = True
                if token:
                    tokens.append(token)
                    token = ""
                tokens.append(c)  # Оператор
        
        if token:
            tokens.append(token)  # Последнее число в выражении
        
        return tokens
    # Calculate persent and factorial
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
    # Main method for calculate
    async def _calculate_expression_base(self, tokens: list[str]) -> str:
        print(tokens)
        result: Decimal = Decimal(tokens[0])
        last_operator: str = '+'
        token: str
        num: Decimal
        priority_operator_index: int
        while len(tokens) != 1:
            if '*' in tokens:
                priority_operator_index = tokens.index('*')
                b: Decimal = Decimal(tokens.pop(priority_operator_index+1))
                tokens.pop(priority_operator_index)
                a: Decimal = Decimal(tokens[priority_operator_index-1])
                tokens[priority_operator_index-1] = str(a*b)
            elif '/' in tokens:
                priority_operator_index = tokens.index('/')
                b: Decimal = Decimal(tokens.pop(priority_operator_index+1))
                tokens.pop(priority_operator_index)
                a: Decimal = Decimal(tokens[priority_operator_index-1])
                tokens[priority_operator_index-1] = str(a/b)
            elif '-' in tokens:
                priority_operator_index = tokens.index('-')
                b: Decimal = Decimal(tokens.pop(priority_operator_index+1))
                tokens.pop(priority_operator_index)
                a: Decimal = Decimal(tokens[priority_operator_index-1])
                tokens[priority_operator_index-1] = str(a-b)
            elif '+' in tokens:
                priority_operator_index = tokens.index('+')
                b: Decimal = Decimal(tokens.pop(priority_operator_index+1))
                tokens.pop(priority_operator_index)
                a: Decimal = Decimal(tokens[priority_operator_index-1])
                tokens[priority_operator_index-1] = str(a+b)
        return tokens[0]

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

class UI:
    colors_background: list[str] = ["#99FF18", "#FFF818", "#FFA918", "#FF6618", "#FF2018", "#FF1493", "#FF18C9", "#CB18FF", "#9118FF", "#5C18FF", "#1F75FE", "#00BFFF", "#18FFE5", "#00FA9A", "#00FF00", "#7FFF00", "#CEFF1D"]
    
    # Loading css
    @staticmethod
    def apply_css(css: str) -> None:
        # Загрузка CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(css)

        # Применение CSS стилей ко всему приложению
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    @staticmethod
    def window_coloring(button: Gtk.Button = None):
        randomNumber_1: str = random.choice(UI.colors_background)
        randomNumber_2: str = random.choice(UI.colors_background)
        while randomNumber_1 == randomNumber_2:
            randomNumber_2 = random.choice(UI.colors_background)
        UI.apply_css(f"window{{background: linear-gradient(to bottom right, {randomNumber_1}, {randomNumber_2});}} frame{{background: linear-gradient(to bottom right, {randomNumber_1}, {randomNumber_2});}}")



class CustomTitleBar(Gtk.HeaderBar):
    def __init__(self):
        super().__init__()
        self.set_show_title_buttons(True)

        # Кнопка для смены языка
        language_button = Gtk.Button(label="EN")  # Используем текстовую метку
        language_button.connect("clicked", self.on_language_clicked)
        self.pack_start(language_button)

        # Кнопка для изменения цвета фона
        color_fon_button = Gtk.Button(label="Fon")  # Используем текстовую метку
        color_fon_button.connect("clicked", UI.window_coloring)
        self.pack_start(color_fon_button)


    def on_language_clicked(self, button): pass

    def on_close_clicked(self, button):
        Gtk.main_quit()

    def on_minimize_clicked(self, button):
        self.get_window().iconify()

    def on_maximize_clicked(self, button):
        # Альтернативный способ развертывания окна
        window = self.get_window()
        if window.is_maximized():
            window.unmaximize()
        else:
            window.maximize()



class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("Calculator")
        self.set_titlebar(CustomTitleBar()) 
        self.set_default_size(400, 600)
        (main_grid := Gtk.Grid()).set_css_classes(["main_grid"])
        self.set_child(main_grid)
        
        # Создаем контейнер для вкладок
        self.notebook = Gtk.Notebook()
        self.notebook.set_hexpand(True)
        self.notebook.set_vexpand(True)

        main_grid.attach(self.notebook, 0,0,1,1)



        # Создаем вкладки
        self.create_tab("Base", self.graphical_main_calc())
        self.create_tab("Вкладка 2", Gtk.Grid())
        self.create_tab("Вкладка 3", Gtk.Grid())

    def button_for_main_calc(self, label: str, grid: Gtk.Grid, column: int, row: int, width: int = 1, height: int = 1):
        button = Gtk.Button(label = label)
        button.set_css_classes(["keybord-base-calc"])
        grid.attach(button, column, row, width, height)


    def graphical_main_calc(self) -> Gtk.Grid:
        grid_main_calc = Gtk.Grid()
        # button delete all expression
        button_for_main_calc("C", grid_main_calc, 0, 0)
        # entry for input expression
        entry_for_expression = Gtk.Entry()
        entry_for_expression.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(entry_for_expression, 1, 0, 3, 1)
        # button backspace
        button_backspace = Gtk.Button(label = "<-")
        button_backspace.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_backspace, 4, 0, 1, 1)
        # button smart brackets for expression
        button_smart_brackets = Gtk.Button(label = "()")
        button_smart_brackets.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_smart_brackets, 0, 1, 1, 1)
        # button open brackets
        button_open_brackets = Gtk.Button(label = "(")
        button_open_brackets.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_open_brackets, 1, 1, 1, 1)
        # button close brackets
        button_close_brackets = Gtk.Button(label = ")")
        button_close_brackets.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_close_brackets, 2, 1, 1, 1)
        # button modulo
        button_modulo = Gtk.Button(label = "mod")
        button_modulo.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_modulo, 3, 1, 1, 1)
        # button Pi
        button_Pi = Gtk.Button(label = "_Pi")
        button_Pi.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_Pi, 4, 1, 1, 1)
        # button 7
        button_7 = Gtk.Button(label = "7")
        button_7.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_7, 0, 2, 1, 1)
        # button 8
        button_8 = Gtk.Button(label = "8")
        button_8.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_8, 1, 2, 1, 1)
        # button 9
        button_9 = Gtk.Button(label = "9")
        button_9.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_9, 2, 2, 1, 1)
        # button division
        button_division = Gtk.Button(label = "/")
        button_division.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_division, 3, 2, 1, 1)
        # button sqrt
        button_sqrt = Gtk.Button(label = "sqrt")
        button_sqrt.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_sqrt, 4, 2, 1, 1)
        # button 4
        button_4 = Gtk.Button(label = "4")
        button_4.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_4, 0, 3, 1, 1)
        # button 5
        button_5 = Gtk.Button(label = "5")
        button_5.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_5, 1, 3, 1, 1)
        # button 6
        button_6 = Gtk.Button(label = "6")
        button_6.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_6, 2, 3, 1, 1)
        # button multiplication
        button_multiplication = Gtk.Button(label = "*")
        button_multiplication.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_multiplication, 3, 3, 1, 1)
        # button degree
        button_degree = Gtk.Button(label = "^")
        button_degree.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_degree, 4, 3, 1, 1)
        # button 1
        button_1 = Gtk.Button(label = "1")
        button_1.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_1, 0, 4, 1, 1)
        # button 2
        button_2 = Gtk.Button(label = "2")
        button_2.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_2, 1, 4, 1, 1)
        # button 3
        button_3 = Gtk.Button(label = "3")
        button_3.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_3, 2, 4, 1, 1)
        # button minus
        button_minus = Gtk.Button(label = "-")
        button_minus.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_minus, 3, 4, 1, 1)
        # button factorial
        button_factorial = Gtk.Button(label = "!")
        button_factorial.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_factorial, 4, 4, 1, 1)
        # button 0
        button_0 = Gtk.Button(label = "0")
        button_0.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_0, 0, 5, 1, 1)
        # button point
        button_point = Gtk.Button(label = ".")
        button_point.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_point, 1, 5, 1, 1)
        # button persent
        button_persent = Gtk.Button(label = "%")
        button_percent.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_persent, 2, 5, 1, 1)
        # button plus
        button_plus = Gtk.Button(label = "+")
        button_plus.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_plus, 3, 5, 1, 1)
        # button equals
        button_equals = Gtk.Button(label = "=")
        button_equals.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_equals, 4, 5, 1, 2)
        # button log
        button_log = Gtk.Button(label = "log")
        button_log.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_log, 0, 6, 1, 1)
        # button ln
        button_ln = Gtk.Button(label = "ln")
        button_ln.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_ln, 1, 6, 1, 1)
        # button lg
        button_lg = Gtk.Button(label = "lg")
        button_lg.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_lg, 2, 6, 1, 1)
        # button comma
        button_comma = Gtk.Button(label = ",")
        button_comma.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_comma, 3, 6, 1, 1)
        # button a
        button_a = Gtk.Button(label = "a")
        button_a.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_a, 0, 7, 1, 1)
        # button b
        button_b = Gtk.Button(label = "b")
        button_b.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_b, 1, 7, 1, 1)
        # button c
        button_c = Gtk.Button(label = "c")
        button_c.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_c, 2, 7, 1, 1)
        # button 0x
        button_0x = Gtk.Button(label = "0x")
        button_0x.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_0x, 3, 7, 1, 1)
        # button round
        button_round = Gtk.Button(label = "round")
        button_round.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_round, 4, 7, 1, 1)
        # button d
        button_d = Gtk.Button(label = "d")
        button_d.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_d, 0, 8, 1, 1)
        # button e
        button_e = Gtk.Button(label = "e")
        button_e.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_e, 1, 8, 1, 1)
        # button f
        button_f = Gtk.Button(label = "f")
        button_f.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_f, 2, 8, 1, 1)
        # button 0b
        button_0b = Gtk.Button(label = "0b")
        button_0b.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button_0b, 3, 8, 1, 1)
        # button _E
        button__E = Gtk.Button(label = "_E")
        button__E.set_css_class(["keybord-base-calc"])
        grid_main_calc.attach(button__E, 4, 8, 1, 1)

        return grid_main_calc

    def create_tab(self, tab_title, grid_information: Gtk.Grid):
        # Создаем фрейм для вкладки
        (tab_label := Gtk.Label(label=tab_title)).set_css_classes(["calc_mods"])
        # Создаем фрейм для содержимого и задаем CSS класс для его стилизации
        (frame := Gtk.Frame()).set_css_classes(["calc_mods"])
        frame.set_child(grid_information)
        # Добавляем вкладку в контейнер
        self.notebook.append_page(frame, tab_label)


class MyApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.example.myapp")


    def do_activate(self):
        win = MainWindow(self)
        # Загрузка CSS
        UI.apply_css("""
            grid.main_grid {
                background-color: rgba(0, 0, 0, 0);
                color: white;
                margin: 10px;
            }
            frame{
                background-color: rgba(0, 0, 0, 0.3);
                border-radius: 0px;
            }
            /* Стили для всего Notebook */
            .notebook {
                background-color: rgba(0, 0, 0, 0.3);
            }

            /* Стили для вкладок внутри Notebook */
            notebook tab {
                background-color: rgba(0, 0, 0, 0.1);
            }

            notebook header {
                background-color: rgba(0, 0, 0, 0.3);
            }
            .keybord-base-calc{
                border-radius: 0px;
                border-color: rgba(0,0,0,0);
                background-color: rgba(0, 0, 0, 0.3);
            }

        """)
        UI.window_coloring()
        win.present()

app = MyApplication()
app.run()

async def main() -> None:
    CalculateMain_v = CalculateMain()
    while True:
        print(await CalculateMain_v.calc_main(expression = str(input("Input expression :"))))
asyncio.run(main())
