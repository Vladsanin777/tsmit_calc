import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk

# Главный класс приложения
class MyApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.example.myapp")

    def do_activate(self):
        # Создаем и отображаем главное окно
        global main_window_class
        main_window_class = MainWindow(self)
        UI.window_coloring()  # Вызов функции стилизации
        main_window_class.present()

# Окно приложения
class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("MenuButton Example")
        self.set_default_size(400, 200)
        
        # Создаем вертикальный контейнер
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_child(vbox)
        
        # Меню кнопка 1 (Поповер слева)
        menu_button1 = Gtk.MenuButton(label="Menu Button 1")
        menu_button1.add_css_class('custom-button1')
        
        # Поповер для первой кнопки
        popover1 = Gtk.Popover()
        popover_box1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        popover1.set_child(popover_box1)
        popover1.set_position(Gtk.PositionType.LEFT)  # Устанавливаем позицию поповера слева
        
        popover_box1.append(Gtk.Label(label="Option 1.1"))
        popover_box1.append(Gtk.Label(label="Option 1.2"))
        popover_box1.append(Gtk.Label(label="Option 1.3"))
        
        menu_button1.set_popover(popover1)
        
        # Меню кнопка 2 (Поповер снизу)
        menu_button2 = Gtk.MenuButton(label="Menu Button 2")
        menu_button2.add_css_class('custom-button2')
        
        # Поповер для второй кнопки
        popover2 = Gtk.Popover()
        popover_box2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        popover2.set_child(popover_box2)
        popover2.set_position(Gtk.PositionType.BOTTOM)  # Устанавливаем позицию поповера снизу
        
        popover_box2.append(Gtk.Label(label="Option 2.1"))
        popover_box2.append(Gtk.Label(label="Option 2.2"))
        popover_box2.append(Gtk.Label(label="Option 2.3"))
        
        menu_button2.set_popover(popover2)
        
        # Добавляем элементы в контейнер
        vbox.append(menu_button1)
        vbox.append(menu_button2)

# Класс для стилизации окна
class UI:
    @staticmethod
    def window_coloring():
        # Установка CSS стилей
        css_provider = Gtk.CssProvider()
        css = b"""
        menubutton.custom-button1 {
            background-color: #e0f7fa;
            color: #004d40;
            font-size: 14px;
            padding: 10px;
            border-radius: 10px;
        }

        menubutton.custom-button1:hover {
            background-color: #b2ebf2;
        }

        menubutton.custom-button2 {
            background-color: #ffe0b2;
            color: #e65100;
            font-size: 16px;
            padding: 12px;
            border-radius: 5px;
            font-weight: bold;
        }

        menubutton.custom-button2:hover {
            background-color: #ffcc80;
        }
        """
        css_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

# Запуск приложения
app = MyApplication()
app.run()

