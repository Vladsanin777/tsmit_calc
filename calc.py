import gi
import random
import asyncio
from math import factorial
from decimal import Decimal

gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, Gdk, GObject


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
        UI.apply_css(f"window{{background: linear-gradient(to bottom right, {randomNumber_1}, {randomNumber_2});}}") # frame{{background: linear-gradient(to bottom right, {randomNumber_1}, {randomNumber_2});}}")



class CustomTitleBar(Gtk.HeaderBar):
    def __init__(self):
        super().__init__()
        self.set_show_title_buttons(True)

        # Кнопка для смены языка
        (language_button := Gtk.Button(label="EN")).set_css_classes(["header_element"])  # Используем текстовую метку
        language_button.connect("clicked", self.on_language_clicked)
        self.pack_start(language_button)
        

        # Кнопка для изменения цвета фона
        (color_fon_button := Gtk.Button(label="Fon")).set_css_classes(["header_element"])  # Используем текстовую метку
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

    _grid_main_calc: Gtk.Grid
    notebook: Gtk.Notebook

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


        self.graphical_main_calc()

        # Создаем вкладки
        self.create_tab(self.notebook, "Base", self._grid_main_calc)
        self.create_tab(self.notebook, "Вкладка 2", Gtk.Grid())
        self.create_tab(self.notebook, "Вкладка 3", Gtk.Grid())

    def button_for_main_calc(self, label: str, grid: Gtk.Grid, column: int, row: int, width: int = 1, height: int = 1) -> None:
        button = Gtk.Button(label = label)
        button.set_css_classes(["keybord-base-calc"])
        button.set_name(f"{label}")
        grid.attach(button, column, row, width, height)
        # Настройка DragSource для каждой кнопки
        drag_source = Gtk.DragSource()
        drag_source.connect("prepare", self.on_drag_prepare)
        button.add_controller(drag_source)
        button.set_hexpand(True)
        button.set_vexpand(True)
    # Adding place for button
    def add_cell_for_button(self, label_button, column: int, row: int) -> None:
        cell: Gtk.Box = Gtk.Box(spacing=0, orientation=Gtk.Orientation.VERTICAL)
        self._grid_main_calc.attach(cell, column, row, 1, 1)
        cell.set_hexpand(True)
        cell.set_vexpand(True)
        drop_target: Gtk.DropTarget = Gtk.DropTarget.new(GObject.TYPE_STRING, Gdk.DragAction.COPY)
        drop_target.connect("drop", self.on_drop)
#        drop_target.set_hexpand(True)
#        drop_target.set_vexpand(True)
#        drop_target.set_css_classes(["drop-target-cell-button"])
        drop_target.set_name("drop-targer-all")
        cell.set_css_classes(["drop-target-cell-button-box"])
        cell.add_controller(drop_target)

        self.add_basic_main_button(label_button, cell)
        

    # Обработка получения кнопки в ячейке
    def on_drop(self, drop_target, label, x, y) -> bool:
        # Определяем, к какой ячейке произошло перетаскивание
        cell = drop_target.get_widget()  # Получаем ячейку, в которую дропнули
        
        # Проверка на наличие уже существующей кнопки в ячейке
        if (current_button := cell.get_first_child()) is not None:
            cell.remove(current_button)

        self.add_basic_main_button(label, cell)
        

    def add_basic_main_button(self, label: str, cell: Gtk.Box()) -> None:
        # Создаем новую кнопку с тем же именем и добавляем в целевую ячейку
        new_button = Gtk.Button(label=label)

        new_button.set_hexpand(True)
        new_button.set_vexpand(True)

        new_button.set_css_classes(["keybord-base-calc"])
        cell.append(new_button)  # Добавляем кнопку в целевую ячейку
        
        return True


    def row_and_column_index_for_cell(self, count_row: int = 5, count_column: int = 5, start_column: int = 0, start_row: int = 1) -> None:
        labels_buttons_defalut: list[str] = ["()", "(", ")", "mod", "_PI", "7", "8", "9", ":", "sqrt", "4", "5", "6", "*", "^", "1", "2", "3", "-", "!", "0", ".", "%", "+", "="]
        i: int = 0
        for row in range(start_row, count_row + start_row):
            for column in range(start_column, count_column + start_column):
                self.add_cell_for_button(labels_buttons_defalut[i], column, row)
                i += 1

    def graphical_main_calc(self) -> None:
        self._grid_main_calc = Gtk.Grid()
        # button delete all expression
        self.button_for_main_calc("C", self._grid_main_calc, 0, 0)
        # entry for input expression
        entry_for_expression = Gtk.Entry()
        entry_for_expression.set_css_classes(["keybord-base-calc"])
        self._grid_main_calc.attach(entry_for_expression, 1, 0, 3, 1)
        # button backspace
        self.button_for_main_calc("<-", self._grid_main_calc, 4, 0)
        # Creating place for button for drag and drop
        self.row_and_column_index_for_cell()
        """
        # button smart brackets for expression
        self.button_for_main_calc("()", self._grid_main_calc, 0, 1)
        # button open brackets
        self.button_for_main_calc("(", self._grid_main_calc, 1, 1)
        # button close brackets
        self.button_for_main_calc(")", self._grid_main_calc, 2, 1)
        # button modulo
        self.button_for_main_calc("mod", self._grid_main_calc, 3, 1)
        # button Pi
        self.button_for_main_calc("_Pi", self._grid_main_calc, 4, 1)
        # button 7
        self.button_for_main_calc("7", self._grid_main_calc, 0, 2)
        # button 8
        self.button_for_main_calc("8", self._grid_main_calc, 1, 2)
        # button 9
        self.button_for_main_calc("9", self._grid_main_calc, 2, 2)
        # button division
        self.button_for_main_calc("/", self._grid_main_calc, 3, 2)
        # button sqrt
        self.button_for_main_calc("sqrt", self._grid_main_calc, 4, 2)
        # button 4
        self.button_for_main_calc("4", self._grid_main_calc, 0, 3)
        # button 5
        self.button_for_main_calc("5", self._grid_main_calc, 1, 3)
        # button 6
        self.button_for_main_calc("6", self._grid_main_calc, 2, 3)
        # button multiplication
        self.button_for_main_calc("*", self._grid_main_calc, 3, 3)
        # button degree
        self.button_for_main_calc("^", self._grid_main_calc, 4, 3)
        # button 1
        self.button_for_main_calc("1", self._grid_main_calc, 0, 4)
        # button 2
        self.button_for_main_calc("2", self._grid_main_calc, 1, 4)
        # button 3
        self.button_for_main_calc("3", self._grid_main_calc, 2, 4)
        # button minus
        self.button_for_main_calc("-", self._grid_main_calc, 3, 4)
        # button factorial
        self.button_for_main_calc("!", self._grid_main_calc, 4, 4)
        # button 0
        self.button_for_main_calc("0", self._grid_main_calc, 0, 5)
        # button point
        self.button_for_main_calc(".", self._grid_main_calc, 1, 5)
        # button persent
        self.button_for_main_calc("%", self._grid_main_calc, 2, 5)
        # button plus
        self.button_for_main_calc("+", self._grid_main_calc, 3, 5)
        # button equals
        self.button_for_main_calc("=", self._grid_main_calc, 4, 5, 1, 2)
        # button log
        self.button_for_main_calc("log", self._grid_main_calc, 0, 6)
        # button ln
        self.button_for_main_calc("ln", self._grid_main_calc, 1, 6)
        # button lg
        self.button_for_main_calc("lg", self._grid_main_calc, 2, 6)
        # button comma
        self.button_for_main_calc(",", self._grid_main_calc, 3, 6)
        # button a
        self.button_for_main_calc("a", self._grid_main_calc, 0, 7)
        # button b
        self.button_for_main_calc("b", self._grid_main_calc, 1, 7)
        # button c
        self.button_for_main_calc("c", self._grid_main_calc, 2, 7)
        # button 0x
        self.button_for_main_calc("0x", self._grid_main_calc, 3, 7)
        # button round
        self.button_for_main_calc("round", self._grid_main_calc, 4, 7)
        # button d
        self.button_for_main_calc("d", self._grid_main_calc, 0, 8)
        # button e
        self.button_for_main_calc("e", self._grid_main_calc, 1, 8)
        # button f
        self.button_for_main_calc("f", self._grid_main_calc, 2, 8)
        # button 0b
        self.button_for_main_calc("0b", self._grid_main_calc, 3, 8)
        # button _E
        self.button_for_main_calc("_E", self._grid_main_calc, 4, 8)
        """
        self.notebook_basic = Gtk.Notebook()
        self.notebook_basic.set_hexpand(True)
        self.notebook_basic.set_vexpand(True)
        self._grid_main_calc.attach(self.notebook_basic, 0 , 6, 5, 4)
        self._grid_basic_calc_digit_10 = Gtk.Grid()
        self._grid_f_basic_calc_digit_10()
        self._grid_basic_calc_operators = Gtk.Grid()
        self._grid_f_basic_calc_operators()
        self._grid_basic_calc_consts = Gtk.Grid()
        self._grid_f_basic_calc_consts()
        self._grid_basic_calc_others = Gtk.Grid()
        self._grid_f_basic_calc_others()

        self.create_tab(self.notebook_basic, "digits 10", self._grid_basic_calc_digit_10)
        self.create_tab(self.notebook_basic, "operators", self._grid_basic_calc_operators)

        self.create_tab(self.notebook_basic, "others", self._grid_basic_calc_others)

        self.create_tab(self.notebook_basic, "consts", self._grid_basic_calc_consts)

    def _grid_f_basic_calc_others(self) -> None:
        for i, (column, row) in {"round": [0, 0], "mod": [1, 0], "0x": [2, 0], "0b": [3, 0], "0": [4, 0]}.items():
            self.button_for_main_calc(i, self._grid_basic_calc_others, column, row)

    def _grid_f_basic_calc_consts(self) -> None:
        for i, (column, row) in {"_PI": [0, 0], "_E": [1, 0]}.items():
            self.button_for_main_calc(i, self._grid_basic_calc_consts, column, row)


    def _grid_f_basic_calc_operators(self) -> None:
        for i, (column, row) in {"+": [0, 0], "-": [1, 0], ":": [2, 0], "*": [3, 0], "^": [4, 0], "!": [0, 1], "sqrt": [1, 1], "ln": [2, 1], "log": [3, 1], "lg": [4, 1]}.items():
            self.button_for_main_calc(i, self._grid_basic_calc_operators, column, row)

    def _grid_f_basic_calc_digit_10(self) -> None:
        for i, (column, row) in {"1": [0, 0], "2": [1, 0], "3": [2, 0], "4": [3, 0], "5": [4, 0], "6": [0, 1], "7": [1, 1], "8": [2, 1], "9": [3, 1], "0": [4, 1]}.items():
            self.button_for_main_calc(i, self._grid_basic_calc_digit_10, column, row)


    def create_tab(self, notebook, tab_title, grid_information: Gtk.Grid):
        # Создаем фрейм для вкладки
        (tab_label := Gtk.Label(label=tab_title)).set_css_classes(["calc_mods"]) 
        tab_label.set_hexpand(True)
        tab_label.set_vexpand(True)
        # Добавляем вкладку в контейнер
        notebook.append_page(grid_information, tab_label)
    # Подготовка данных для перетаскивания (отправляем имя кнопки)
    def on_drag_prepare(self, drag_source, x, y):
        button = drag_source.get_widget()  # Получаем кнопку, с которой начинается DnD
        return Gdk.ContentProvider.new_for_value(button.get_name())  # Возвращаем уникальное имя кнопки как данные

    
class MyApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.example.myapp")


    def do_activate(self):
        win = MainWindow(self)
        # Загрузка CSS
        UI.apply_css("""
            #drop-target-all {
                margin: 0px;
                border: none;
            }
            grid.main_grid {
                background-color: rgba(0, 0, 0, 0);
                color: white;
                border: none;
            }
            
            /* Стили для всего Notebook */
            notebook {
                border: none;
                outline: none;
                background-color: transparent;
                background: transparent;
            }

            /* Стили для вкладок внутри Notebook */
            notebook tab {
                background: rgba(0, 0, 0, 0.45);
                color: white;
                margin: 5px;
            }
            notebook tab:hover{
                color: black;
                border: none;
                border-color: black;
                background: rgba(0, 0, 0, 0);
            }
            .titlebar { 
                background-color: rgba(0,0,0,0.45); 
                color: rgb(255,255,255); 
                background-image: none; 
                background-blend-mode: overlay; 
            }
            tab{
                border: none;
            }

            notebook box{
                background-color: transparent;
            }

            notebook header {
                border: none;
                background: transparent;
                margin: 0px;
                padding: 0px;
            }
           
            
            headerbar{
                background-color: transparent;
                border: none;
            }
            .keybord-base-calc{
                margin: 0px;
                color: white;
                border-radius: 0px;
                background: rgba(0, 0, 0, 0.45);
                border: 3px solid rgba(0,0,0,0);
                text-shadow: none;
                box-shadow: none;
                font-size: 24px;
            }
            .drop-target-cell-button{
                margin: 0px;
                color: white;
                border-radius: 0px;
                background: rgba(0, 0, 0, 0.45);
                border: 3px solid rgba(0,0,0,0);
                text-shadow: none;
                box-shadow: none;
                font-size: 24px;
            }
            .drop-target-cell-button-box{
                margin: 0px;
                color: white;
                border-radius: 0px;
                border: none;
                text-shadow: none;
                box-shadow: none;
                font-size: 24px;
            }
            .keybord-base-calc:hover{
                background: rgba(0, 0, 0, 0);
                color: black;
            }
            
            grid {
                background: transparent;
                border: none;
            }
            notebook > stack {
                background-color: transparent;
                border: none;
            }
            button.header_element{
                border-radius: 60px;
                color: white;
                background: transparent;
                border: none;
                box-shadow: none;
            }
            button.header_element:hover{
                background: black;
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
