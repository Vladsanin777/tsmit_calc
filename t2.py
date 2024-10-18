import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk

class MyWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="MenuButton with CSS")

        # Создание MenuButton и установка CSS-класса для самой кнопки
        view_setting_button = Gtk.MenuButton.new()
        view_setting_button.set_css_classes(["menu_button_custom"])  # Применяем класс для MenuButton
        view_setting_button.set_child(Gtk.Label(label="View"))  # Устанавливаем текст кнопки
        self.set_child(view_setting_button)

        # Создание Popover и Grid для элементов внутри
        view_setting_button.set_popover(popover := Gtk.Popover.new())
        grid_header_button = Gtk.Grid()

        # Установка отступов в ноль между строками и столбцами
        grid_header_button.set_row_spacing(0)
        grid_header_button.set_column_spacing(0)
        grid_header_button.set_margin_top(0)
        grid_header_button.set_margin_bottom(0)
        grid_header_button.set_margin_start(0)
        grid_header_button.set_margin_end(0)

        popover.set_child(grid_header_button)
        grid_header_button.attach(Gtk.Button(label="general\nhistory"), 0, 0, 1, 1)
        grid_header_button.attach(Gtk.Button(label="local\nhistory"), 0, 1, 1, 1)

        # Применение CSS к самой кнопке и popover
        css_provider = Gtk.CssProvider()
        css = """
        .menu_button_custom {
            background-color: #4CAF50;  /* Зеленый фон для MenuButton */
            color: #FFFFFF;
            padding: 10px;
            border-radius: 5px;
            border: none;
        }
        
        .menu_button_custom > .child {
            color: #FFFFFF;  /* Применение белого цвета к тексту */
        }
        
        .menu_button_custom:hover {
            background-color: #45a049;  /* Темно-зеленый фон при наведении */
        }

        /* Стили для popover */
        popover.background {
            background: transparent;  /* Прозрачный фон для popover */
        }

        popover.contents {
            background-color: #f0f0f0;  /* Светлый фон для содержимого */
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);  /* Тень для содержимого */
            border-radius: 5px;
        }

        popover arrow {
            background-color: #f0f0f0;  /* Цвет стрелки совпадает с фоном содержимого */
            border-bottom-width: 2px;
        }

        button {
            background-color: #4CAF50;  /* Зеленый фон для всех кнопок */
            color: #FFFFFF;
            border-radius: 3px;
            padding: 5px;
            border: none;
        }
        button:hover {
            background-color: #45a049;  /* Темно-зеленый фон при наведении */
        }

        /* Убираем отступы между кнопками в popover */
        grid, button {
            margin: 0;
            padding: 0;
        }
        """
        css_provider.load_from_data(css.encode())

        # Применение CSS-провайдера через дисплей
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

        # Установка размеров окна
        self.set_default_size(300, 200)

class MyApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.example.myapp")
    
    def do_activate(self):
        win = MyWindow(self)
        win.present()

app = MyApplication()
app.run()

