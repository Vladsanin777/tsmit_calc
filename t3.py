import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

class NestedMenuExample(Gtk.Window):
    def __init__(self):
        super().__init__(title="Nested Menu Example")
        self.set_default_size(300, 200)

        # Создаем кнопку для открытия меню
        menu_button = Gtk.Button(label="Open Menu")
        menu_button.connect("clicked", self.on_menu_button_clicked)

        # Добавляем кнопку в окно
        self.set_child(menu_button)

    def on_menu_button_clicked(self, button):
        # Создаем Popover для основного меню
        popover = Gtk.Popover.new(button)

        # Создаем Box для размещения элементов меню
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        # Элемент основного меню
        item1 = Gtk.Button(label="Item 1")
        item1.connect("clicked", self.on_item1_activate)
        box.append(item1)

        # Создаем подменю
        submenu_button = Gtk.Button(label="Submenu")
        box.append(submenu_button)

        # Создаем Popover для подменю
        submenu_popover = Gtk.Popover.new(submenu_button)
        submenu_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        subitem1 = Gtk.Button(label="Subitem 1")
        subitem1.connect("clicked", self.on_subitem1_activate)
        submenu_box.append(subitem1)

        subitem2 = Gtk.Button(label="Subitem 2")
        subitem2.connect("clicked", self.on_subitem2_activate)
        submenu_box.append(subitem2)

        submenu_popover.set_child(submenu_box)

        # Обработчик для открытия подменю
        submenu_button.connect("clicked", lambda x: submenu_popover.popup_at_pointer(x))

        popover.set_child(box)
        popover.popup_at_pointer(button)

    def on_item1_activate(self, widget):
        print("Item 1 activated")

    def on_subitem1_activate(self, widget):
        print("Subitem 1 activated")

    def on_subitem2_activate(self, widget):
        print("Subitem 2 activated")

win = NestedMenuExample()
win.connect("destroy", Gtk.main_quit)  # Здесь используем Gtk.main_quit напрямую
win.show()
Gtk.main()

