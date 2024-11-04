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
    expression: str
    def __init__(self, expression):
        self.expression = expression.replace(" ", "")

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
            elif ':' in tokens:
                priority_operator_index = tokens.index(':')
                b: Decimal = Decimal(tokens.pop(priority_operator_index+1))
                tokens.pop(priority_operator_index)
                a: Decimal = Decimal(tokens[priority_operator_index-1])
                tokens[priority_operator_index-1] = str(a/b)
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
    async def calc(self) -> str:
        if not (await self._equality_of_two_numbers(await self._counting_parentheses(self.expression))):
            raise UnequalNumberOfParenthesesException()
        
        expression_1 = self.expression
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
            Gtk.STYLE_PROVIDER_PRIORITY_USER
        )
    @staticmethod
    def window_coloring(button: Gtk.Button = None):
        randomNumber_1: str = random.choice(UI.colors_background)
        randomNumber_2: str = random.choice(UI.colors_background)
        while randomNumber_1 == randomNumber_2:
            randomNumber_2 = random.choice(UI.colors_background)
        UI.apply_css(f"window{{background: linear-gradient(to bottom right, {randomNumber_1}, {randomNumber_2});}}") # frame{{background: linear-gradient(to bottom right, {randomNumber_1}, {randomNumber_2});}}")

scrolled_window_general_histori: Gtk.ScrolledWindow = Gtk.ScrolledWindow()
add_general_histori: Gtk.Box = Gtk.Box()
scrolled_window_local_histori_basic: Gtk.ScrolledWindow = Gtk.ScrolledWindow()
add_local_histori_basic: Gtk.Box = Gtk.Box()
entry_calc_basic: Gtk.Entry = Gtk.Entry()
set_for_result_basic_calc: Gtk.Label = Gtk.Label()
result_basic_calc: str = "0"

class LogicCalcBasic():
    entry_text: str = ""

    def __init__(self, entry_text: str):
        self.entry_text = entry_text

    def button__ALL(self):
        global add_general_histori, add_local_histori_basic, result_basic_calc, entry_calc_basic
        if (entry_text := "".join(self.entry_text.split("_ALL"))) != "":
            add_general_histori.append(BoxHistoriElement(entry_text, str(result_basic_calc)))
            add_local_histori_basic.append(BoxHistoriElement(entry_text, str(result_basic_calc)))
        entry_calc_basic.set_text("")

        
    def button__DO(self):
        global add_general_histori, add_local_histori_basic, result_basic_calc, entry_calc_basic
        if (entry_text := "".join(entry_text_list := self.entry_text.split("_DO"))) != "":
            add_general_histori.append(BoxHistoriElement(entry_text, str(result_basic_calc)))
            add_local_histori_basic.append(BoxHistoriElement(entry_text, str(result_basic_calc)))
        entry_calc_basic.set_text(entry_text_list[1])

    def button__POST(self):
        global add_general_histori, add_local_histori_basic, result_basic_calc, entry_calc_basic
        if (entry_text := "".join(entry_text_list := entry_calc_basic.get_text().split("_POST"))) != "":
            add_general_histori.append(BoxHiskoriElement(entry_text, str(result_basic_calc)))
            add_local_histori_basic.append(BoxHistoriElement(entry_text, str(result_basic_calc)))
        entry_calc_basic.set_text(entry_text_list[0])

    @staticmethod
    def inputing_entry(button: Gtk.Button, label_button: str) -> None:
        global entry_calc_basic
        position_cursor: int = entry_calc_basic.get_position()
        entry_calc_basic.insert_text(label_button, position_cursor)
        entry_calc_basic.set_position(position_cursor + len(label_button))

    def button_result(self):
        global add_general_histori, add_local_histori_basic, result_basic_calc, entry_calc_basic
        if (entry_text := "".join(entry_text_list := self.entry_text.split("="))) != "":
            add_general_histori.append(BoxHistoriElement(entry_text, str(result_basic_calc)))
            add_local_histori_basic.append(BoxHistoriElement(entry_text, str(result_basic_calc)))
        entry_calc_basic.set_text(result_basic_calc)
        entry_calc_basic.set_position(len(result_basic_calc)-1)


    def button__O(self) -> None:
        global entry_calc_basic
        if (entry_text := "".join(entry_text_list := self.entry_text.split("_O"))) != "":
            element_position = len(entry_text_list[0])-1
            print(element_position, "22")
            entry_calc_basic.set_text(self.entry_text[:element_position] + self.entry_text[element_position+3:])
            
    def button_other(self) -> None:
        global set_for_result_basic_calc, result_basic_calc
        result_basic_calc = asyncio.run(CalculateMain(self.entry_text).calc())
        set_for_result_basic_calc.set_text(result_basic_calc)
""" 
class EmptyElementForHistori(Gtk.Box):
    def __init__(self):
        super().__init__()

        self.set_hexpand(True)
        self.set_vexpand(True)
        self.add_css_class("histori-element")

class BoxForElementsHistori(Gtk.Box):
    def __init__(self):
        super().__init__(spacing=0, orientation=Gtk.Orientation.VERTICAL)
        self.append(EmptyElementForHistori())
"""
class ScrolledWindowHistori(Gtk.ScrolledWindow):
    def __init__(self):
        super().__init__()
        self.add_histori = Gtk.Box(spacing=0, orientation=Gtk.Orientation.VERTICAL)
        self.set_child(self.add_histori)
        self.set_hexpand(True)
        self.set_vexpand(True)

class DragSourceForLabelButtonCalcBasic(Gtk.DragSource):
    def __init__(self):
        super().__init__()
        self.connect("prepare", self.on_drag_prepare)

    def on_drag_prepare(self, drag_source, x, y):
        return Gdk.ContentProvider.new_for_value(drag_source.get_widget().get_label())  # Возвращаем уникальное имя кнопки как данные

class LabelForButtonCalcBasic(Gtk.Label):
    def __init__(self, label: str, css_class: str = None):
        super().__init__(label = label)
        if css_class: self.add_css_class(css_class)
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.add_controller(DragSourceForLabelButtonCalcBasic())

class ButtonForCalcBasic(Gtk.Button):
    def __init__(self, label: str, css_class: str = "keybord-base-calc", callback = None):
        super().__init__()
        if not callback: callback = LogicCalcBasic.inputing_entry
        self.set_child(LabelForButtonCalcBasic(label, css_class))
        self.add_css_class(css_class)
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.connect("clicked", callback, label)

class BoxHistoriElement(Gtk.Box):
    def __init__(self, expression: str, result: str):
        super().__init__(spacing=0, orientation=Gtk.Orientation.HORIZONTAL)
        self.append(LabelForButtonCalcBasic(expression, "histori-element"))
        self.append(LabelForButtonCalcBasic("=", "histori-element"))
        self.append(LabelForButtonCalcBasic(result, "histori-element"))

class EntryCalcBasic(Gtk.Entry):
    def __init__(self):
        super().__init__()
        self.add_css_class("keybord-base-calc")
        self.connect("changed", self.on_entry_changed)
    def on_entry_changed(self, entry):
        if (text_entry := entry.get_text()):
            logic_calc_basic = LogicCalcBasic(text_entry)
            if "_ALL" in text_entry:
                logic_calc_basic.button__ALL()
            elif "_DO" in text_entry:
                logic_calc_basic.button__DO()
            elif "_POST" in text_entry:
                logic_calc_basic.button__POST()
            elif "_O" in text_entry:
                logic_calc_basic.button__O()
            elif "=" in text_entry:
                logic_calc_basic.button_result()
            else:
                logic_calc_basic.button_other()

class DropTargetCalcBasic(Gtk.DropTarget):
    def __init__(self):
        super().__init__()
        self.set_gtypes([GObject.TYPE_STRING])
        self.set_actions(Gdk.DragAction.COPY)
        self.connect("drop", self.on_drop)
#        self.add_css_class("drop-targer-all")
    def on_drop(self, drop_target, label, x, y) -> bool:
        # Определяем, к какой ячейке произошло перетаскивание
        cell = drop_target.get_widget()  # Получаем ячейку, в которую дропнули
        
        # Проверка на наличие уже существующей кнопки в ячейке
        if (current_button := cell.get_first_child()) is not None:
            cell.remove(current_button)
        
        cell.append(ButtonForCalcBasic(label))

class BoxForDropTargetCalcBasic(Gtk.Box):
    def __init__(self, label_button, drop_target: bool = True):
        super().__init__(spacing=0, orientation=Gtk.Orientation.VERTICAL)
        self.set_hexpand(True)
        self.set_vexpand(True)
        if drop_target: self.add_controller(DropTargetCalcBasic())
        self.add_css_class("drop-target-cell-button-box")
        self.append(ButtonForCalcBasic(label_button, "keybord-base-calc"))

class BuildingButtonInGrid():
    def __init__(self, list_button: list[list[str]], grid: Gtk.Grid, row: int = 0):
        for row_labels_for_button in list_button:
            column: int = 0
            for one_button in row_labels_for_button:
                grid.attach(BoxForDropTargetCalcBasic(one_button, True), column, row, 1, 1)
                column += 1
            row += 1

class GridCalcBasicKeybord(Gtk.Grid):
    def __init__(self, list_button: list[list[str]]):
        super().__init__()
        BuildingButtonInGrid(list_button, self)
        

class NotebookCalcBasic(Gtk.Notebook):
    def __init__(self):
        super().__init__()
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.append_page(GridCalcBasicKeybord([["1", "2", "3", "4", "5"], ["6", "7", "8", "9", "0"]]), LabelForButtonCalcBasic("digits 10"))
        self.append_page(GridCalcBasicKeybord([["A", "B", "C"], ["D", "E", "F"]]), LabelForButtonCalcBasic("digits 16"))
        self.append_page(GridCalcBasicKeybord([["+", "-", ":", "*", "^"], ["!", "sqrt", "ln", "log", "lg"]]), LabelForButtonCalcBasic("operators"))
        self.append_page(GridCalcBasicKeybord([["_E", "_PI"]]), LabelForButtonCalcBasic("consts"))
        self.append_page(GridCalcBasicKeybord([["round", "mod", "0x"], ["0b", "0", ","]]), LabelForButtonCalcBasic("other"))

class GridCalcBasic(Gtk.Grid):
    def __init__(self):
        global entry_calc_basic, box_local_histori_basic, add_local_histori_basic, set_for_result_basic_calc, result_basic_calc
        super().__init__()
        self.attach(box_local_histori_basic := ScrolledWindowHistori(), 0, 0, 5, 3)

        add_local_histori_basic = box_local_histori_basic.add_histori

        self.button_for_calc_basic("_ALL", 0, 3)
        
        self.attach(entry_calc_basic := EntryCalcBasic(), 1, 3, 3, 1)

        self.button_for_calc_basic("_O", 4, 3)
        
        BuildingButtonInGrid([["()", "(", ")", "mod", "_PI"], ["7", "8", "9", ":", "sqrt"], ["4", "5", "6", "*", "^"], ["1", "2", "3", "-", "!"], ["0", ".", "%", "+", "_E"]], self, 4)

        self.attach(set_for_result_basic_calc := ButtonForCalcBasic(result_basic_calc, "keybord-base-calc"), 0, 9, 2, 1)

        set_for_result_basic_calc = set_for_result_basic_calc.get_child()

        self.button_for_calc_basic("_DO", 2, 9)
        self.button_for_calc_basic("_POST", 3, 9)
        self.button_for_calc_basic("=", 4, 9)

        self.attach(NotebookCalcBasic(), 0 , 10, 5, 4)
        
        self.set_hexpand(True)
        self.set_vexpand(True)

    def button_for_calc_basic(self, label: str, column: int, row: int) -> None:
        self.attach(ButtonForCalcBasic(label, "keybord-base-calc", None), column, row, 1, 1)

class NotebookMain(Gtk.Notebook):
    def __init__(self):
        super().__init__()
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.append_page(GridCalcBasic(), LabelForButtonCalcBasic("Basic"))
        self.append_page(Gtk.Grid(), LabelForButtonCalcBasic("Tab 2"))
        self.append_page(Gtk.Grid(), LabelForButtonCalcBasic("Tab 3"))


class GridMain(Gtk.Grid):
    def __init__(self):
        super().__init__()
        global scrolled_window_general_histori, add_general_histori
        self.add_css_class("main_grid")
        self.attach(scrolled_window_general_histori := ScrolledWindowHistori(), 0, 0, 1, 4)
        add_general_histori = scrolled_window_general_histori.add_histori
        self.attach(NotebookMain(), 0, 4, 1, 10)


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("Calculator")
        self.set_titlebar(CustomTitleBar()) 
        self.set_default_size(400, 800)
        self.set_child(GridMain())
        
###############################################################

#TitleBar

class LebalMenuButtonTitlebar(Gtk.Label):
    def __init__(self, label):
        super().__init__(label = label)

class ButtonTitleBar(Gtk.Button):
    def __init__(self, label, callback, css_class: str = "header_element"):
        super().__init__(label = label)
        self.connect("clicked", callback)
        if css_class: self.add_css_class(css_class)

class GridLocalHistoriTitleBar(Gtk.Grid):
    def __init__(self):
        super().__init__()

        self.attach(ButtonTitleBar("Basic", self.button_settings_view_local_histori_basic, None), 0, 0, 1, 1)
        self.attach(ButtonTitleBar("Tab 2", self.button_settings_view_local_histori_tab_2, None), 0, 1, 1, 1)
        self.attach(ButtonTitleBar("Tab 3", self.button_settings_view_local_histori_tab_3, None), 0, 2, 1, 1)

    def button_settings_view_local_histori_basic(self, button) -> None:
        global box_local_histori_basic
        box_local_histori_basic.set_visible(not box_local_histori_basic.is_visible())
    
    def button_settings_view_local_histori_tab_2(self, button) -> None:
        pass

    def button_settings_view_local_histori_tab_3(self, button) -> None:
        pass


class PopoverLocalHistoriTitleBar(Gtk.Popover):
    def __init__(self):
        super().__init__()
        self.set_child(GridLocalHistoriTitleBar())
        self.set_css_classes(["header_popover_menu_button"])
    def on_button(self):
        self.set_position(Gtk.PositionType.LEFT)

class MenuButtonLocalHistoriTitleBar(Gtk.MenuButton):
    def __init__(self, label):
        super().__init__()
        self.set_popover(popover := PopoverLocalHistoriTitleBar())
        popover.on_button()
        self.set_child(LebalMenuButtonTitlebar("local\nhistori"))
        self.add_css_class("in_popover")

class GridMainTitleBar(Gtk.Grid):
    def __init__(self):
        super().__init__()
        self.set_vexpand(True)
        self.set_hexpand(True)
        self.attach(ButtonTitleBar("general\nhistori", self.button_settings_view_general_histori, None), 0, 0, 1, 1)
        self.attach(MenuButtonLocalHistoriTitleBar("local\nhistori"), 0, 1, 1, 1)
    
    def button_settings_view_general_histori(self, button: Gtk.Button) -> None:
        global scrolled_window_general_histori
        # Set the visibility based on the current state
        scrolled_window_general_histori.set_visible(not scrolled_window_general_histori.is_visible())


class PopoverMainTitleBar(Gtk.Popover):
    def __init__(self):
        super().__init__()
        self.set_position(Gtk.PositionType.BOTTOM)
        self.set_child(GridMainTitleBar())
        self.set_css_classes(["header_popover_menu_button"])

class MenuButtonMainTitleBar(Gtk.MenuButton):
    def __init__(self, label: str):
        super().__init__()
        self.set_popover(PopoverMainTitleBar())
        self.set_child(Gtk.Label(label = "View"))
        self.add_css_class("header_element")


class CustomTitleBar(Gtk.HeaderBar):
    def __init__(self):
        super().__init__()
        self.set_show_title_buttons(True)

        # Кнопка для смены языка
        self.pack_start(ButtonTitleBar("EN", self.on_language_clicked))

        # Кнопка для изменения цвета фона
        self.pack_start(ButtonTitleBar("Fon", UI.window_coloring))

        self.pack_end(MenuButtonMainTitleBar("Veiw"))

    def on_language_clicked(self, button) -> None: pass

    
class MyApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.example.myapp")


    def do_activate(self):
        global main_window_class
        main_window_class = MainWindow(self)
        # Загрузка CSS
        style_provider = Gtk.CssProvider()
        style_provider.load_from_path("styles.css")

        # Примените стили к вашему приложению
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), 
            style_provider, 
            Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

        UI.window_coloring()
        main_window_class.present()

app = MyApplication()
app.run()

async def main() -> None:
    CalculateMain_v = CalculateMain()
    while True:
        print(await CalculateMain_v.calc_main(expression = str(input("Input expression :"))))
asyncio.run(main())
