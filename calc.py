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
            Gtk.STYLE_PROVIDER_PRIORITY_USER
        )
    @staticmethod
    def window_coloring(button: Gtk.Button = None):
        randomNumber_1: str = random.choice(UI.colors_background)
        randomNumber_2: str = random.choice(UI.colors_background)
        while randomNumber_1 == randomNumber_2:
            randomNumber_2 = random.choice(UI.colors_background)
        UI.apply_css(f"window{{background: linear-gradient(to bottom right, {randomNumber_1}, {randomNumber_2});}}") # frame{{background: linear-gradient(to bottom right, {randomNumber_1}, {randomNumber_2});}}")

box_general_histori = None
add_general_histori = None
box_local_histori_basic = None
add_local_histori_basic = None
entry_calc_basic = None

class EmptyElementForHistori(Gtk.Grid):
    def __init__(self):
        super().__init__()

        self.set_hexpand(True)
        self.set_vexpand(True)
        self.add_css_class("histori-element")

class ScrolledWindowHistori(Gtk.ScrolledWindow):
    def __init__(self):
        super().__init__()
        self.set_child(EmptyElementForHistori())


class BoxHistori(Gtk.Box):
    add_histori: Gtk.ScrolledWindow = None
    def __init__(self):
        super().__init__(spacing=0, orientation=Gtk.Orientation.VERTICAL)
        self.add_histori = ScrolledWindowHistori()
        self.append(self.add_histori)
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
        if not callback: callback = self.inputing_entry
        self.set_child(LabelForButtonCalcBasic(label, css_class))
        self.add_css_class(css_class)
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.connect("clicked", callback, label)
    def inputing_entry(self, button: Gtk.Button, label_button: str) -> None:
        global entry_calc_basic
        entry_calc_basic.set_text(entry_calc_basic.get_text() + label_button)    

class EntryCalcBasic(Gtk.Entry):
    def __init__(self):
        super().__init__()
        self.add_css_class("keybord-base-calc")

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

class GridCalcBasicKeybord(Gtk.Grid):
    def __init__(self, list_button: list[list[str]]):
        super().__init__()
        column: int = 0
        row: int = 0
        for row_labels_for_button in list_button:
            for one_button in row_labels_for_button:
                self.attach(BoxForDropTargetCalcBasic(one_button, False), column, row, 1, 1)
                column += 1
            column = 0
            row += 1

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
        global entry_calc_basic, box_local_histori_basic, add_lacal_histori_basic
        super().__init__()
        self.attach(box_local_histori_basic := BoxHistori(), 0, 0, 5, 3)

        add_local_histori_basic = box_local_histori_basic.add_histori

        self.button_for_calc_basic("C", 0, 3, self.clear_entry)
        
        self.attach(entry_calc_basic := EntryCalcBasic(), 1, 3, 3, 1)

        self.button_for_calc_basic("<-", 4, 3, self.back_space_entry)

        self.row_and_column_index_for_cell()

        self.attach(NotebookCalcBasic(), 0 , 9, 5, 4)
        
        self.set_hexpand(True)
        self.set_vexpand(True)

    def clear_entry(self, button) -> None:
        global entry_calc_basic
        entry_calc_basic.set_text("")

    def back_space_entry(self, button) -> None:
        global entry_calc_basic
        entry_calc_basic.set_text(entry_calc_basic.get_text()[:-1])

    def button_for_calc_basic(self, label: str, column: int, row: int, callback = None) -> Gtk.Button:
        self.attach(ButtonForCalcBasic(label, "keybord-base-calc", callback if callback else label), column, row, 1, 1)

    def row_and_column_index_for_cell(self, count_row: int = 5, count_column: int = 5, start_column: int = 0, start_row: int = 4) -> None:
        labels_buttons_defalut: list[str] = ["()", "(", ")", "mod", "_PI", "7", "8", "9", ":", "sqrt", "4", "5", "6", "*", "^", "1", "2", "3", "-", "!", "0", ".", "%", "+", "="]
        i: int = 0
        for row in range(start_row, count_row + start_row):
            for column in range(start_column, count_column + start_column):
                self.attach(BoxForDropTargetCalcBasic(labels_buttons_defalut[i]), column, row, 1, 1)
                i += 1


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
        global box_general_histori, add_general_histori
        self.add_css_class("main_grid")
        self.attach(box_general_histori := BoxHistori(), 0, 0, 1, 4)
        add_general_histori = box_general_histori.add_histori
        self.attach(NotebookMain(), 0, 4, 1, 10)


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("Calculator")
        self.set_titlebar(CustomTitleBar()) 
        self.set_default_size(400, 600)
        self.set_child(GridMain())
        
###############################################################

#TitleBar

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
        self.add_css_class("header_popover_menu_button")
        self.set_position(Gtk.PositionType.LEFT)
        self.set_child(GridLocalHistoriTitleBar())

class MenuButtonLocalHistoriTitleBar(Gtk.MenuButton):
    def __init__(self, label):
        super().__init__(label = label)
        self.add_css_class("in_popover")
        self.set_popover(PopoverLocalHistoriTitleBar())

class GridMainTitleBar(Gtk.Grid):
    def __init__(self):
        super().__init__()
        self.attach(ButtonTitleBar("general\nhistori", self.button_settings_view_general_histori, None), 0, 0, 1, 1)
        self.attach(MenuButtonLocalHistoriTitleBar("local\nhistori"), 0, 1, 1, 1)
    
    def button_settings_view_general_histori(self, button) -> None:
        global box_general_histori
        # Set the visibility based on the current state
        box_general_histori.set_visible(not box_general_histori.is_visible())


class PopoverMainTitleBar(Gtk.Popover):
    def __init__(self):
        super().__init__()
        self.add_css_class("header_popover_menu_button")
        self.set_position(Gtk.PositionType.BOTTOM)
        self.set_child(GridMainTitleBar())

class MenuButtonMainTitleBar(Gtk.MenuButton):
    def __init__(self, label: str):
        super().__init__(label = label)
        self.add_css_class("header_element")
        self.set_popover(PopoverMainTitleBar())


class CustomTitleBar(Gtk.HeaderBar):
    def __init__(self):
        super().__init__()
        self.set_show_title_buttons(True)

        # Кнопка для смены языка
        self.pack_start(ButtonTitleBar("EN", self.on_language_clicked))

        # Кнопка для изменения цвета фона
        self.pack_start(ButtonTitleBar("Fon", UI.window_coloring))

        self.pack_end(MenuButtonMainTitleBar("Veiw"))

        view_setting_button = Gtk.MenuButton.new()
        view_setting_button.add_css_class("header_element")
        view_setting_button.set_child(label_menu_button := Gtk.Label(label = "Veiw"))
        self.pack_end(view_setting_button)
        view_setting_button.set_popover(popover_menu_button_view_settings := Gtk.Popover.new())

        popover_menu_button_view_settings.set_css_classes(["header_popover_menu_button"])
        popover_menu_button_view_settings.set_position(Gtk.PositionType.BOTTOM)

        popover_menu_button_view_settings.set_child(grid_header_button_view_settings := Gtk.Grid())
        grid_header_button_view_settings.set_hexpand(True)
        grid_header_button_view_settings.set_vexpand(True)
        grid_header_button_view_settings.attach(button_general_histori := Gtk.Button(label = "general\nhistori"), 0, 0, 1, 1)
        grid_header_button_view_settings.attach(button_local_histori := Gtk.MenuButton.new(), 0, 1, 1, 1)
        button_local_histori.add_css_class("in_popover")
        button_local_histori.set_child(Gtk.Label(label = "local\nhistori"))
        button_general_histori.connect("clicked", self.button_settings_view_general_histori)

        button_local_histori.set_popover(popover_local_histori := Gtk.Popover.new())
        popover_local_histori.set_child(grid_local_histori := Gtk.Grid())
        popover_local_histori.set_position(Gtk.PositionType.LEFT)
        grid_local_histori.set_vexpand(True)
        grid_local_histori.set_hexpand(True)


        popover_local_histori.set_css_classes(["header_popover_menu_button"])

        grid_local_histori.attach(button_local_histori_basic := Gtk.Button(label = "Basic"), 0, 0, 1, 1)
        button_local_histori_basic.connect("clicked", self.button_settings_view_local_histori_basic)


        grid_local_histori.attach(button_local_histori_tab_2 := Gtk.Button(label = "Tab2"), 0, 1, 1, 1)
        button_local_histori_basic.connect("clicked", self.button_settings_view_local_histori_tab_2)

        grid_local_histori.attach(button_local_histori_tab_3 := Gtk.Button(label = "Tab3"), 0, 2, 1, 1)
        button_local_histori_basic.connect("clicked", self.button_settings_view_local_histori_tab_3)
        # !!! Must been For all tab
        
        # Установка отступов в ноль между строками и столбцами
        grid_header_button_view_settings.set_row_spacing(0)
        grid_header_button_view_settings.set_column_spacing(0)
        grid_header_button_view_settings.set_margin_top(0)
        grid_header_button_view_settings.set_margin_bottom(0)
        grid_header_button_view_settings.set_margin_start(0)
        grid_header_button_view_settings.set_margin_end(0)


        # Установка отступов в ноль между строками и столбцами
        grid_local_histori.set_row_spacing(0)
        grid_local_histori.set_column_spacing(0)
        grid_local_histori.set_margin_top(0)
        grid_local_histori.set_margin_bottom(0)
        grid_local_histori.set_margin_start(0)
        grid_local_histori.set_margin_end(0)

        button_general_histori.set_hexpand(True)
        button_general_histori.set_vexpand(True)
        button_local_histori.set_vexpand(True)
        button_local_histori.set_hexpand(True)

    def button_settings_view_general_histori(self, button) -> None:
        global box_general_histori
        # Set the visibility based on the current state
        box_general_histori.set_visible(not box_general_histori.is_visible())

    def button_settings_view_local_histori_basic(self, button) -> None:
        global box_local_histori_basic
        box_local_histori_basic.set_visible(not box_local_histori_basic.is_visible())
    
    def button_settings_view_local_histori_tab_2(self, button) -> None:
        pass

    def button_settings_view_local_histori_tab_3(self, button) -> None:
        pass

    def on_language_clicked(self, button) -> None: pass

    def on_close_clicked(self, button) -> None:
        Gtk.main_quit()

    def on_minimize_clicked(self, button) -> None:
        self.get_window().iconify()

    def on_maximize_clicked(self, button) -> None:
        # Альтернативный способ развертывания окна
        window = self.get_window()
        if window.is_maximized():
            window.unmaximize()
        else:
            window.maximize()



    
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
