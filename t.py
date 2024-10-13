import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk

class DragDropExample(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("Drag and Drop Example")
        self.set_default_size(400, 200)

        # Контейнер
        box = Gtk.Box(spacing=10)
        self.set_child(box)

        # Источник перетаскивания (label1)
        self.label1 = Gtk.Label(label="Drag me!")
        self.label1.set_selectable(True)
        box.append(self.label1)

        # Приёмник перетаскивания (label2)
        self.label2 = Gtk.Label(label="Drop here!")
        box.append(self.label2)

        # Создаём объект DragSource для label1
        drag_source = Gtk.DragSource()
        drag_source.connect("prepare", self.on_drag_prepare)
        self.label1.add_controller(drag_source)

        # Создаём объект DropTarget для label2
        drop_target = Gtk.DropTarget.new(Gdk.FileList, Gdk.DragAction.COPY)
        drop_target.set_gtypes([str])  # Ожидаем строки (текст)
        drop_target.connect("drop", self.on_drop)
        self.label2.add_controller(drop_target)

    # Подготовка данных для перетаскивания
    def on_drag_prepare(self, drag_source, x, y):
        text = self.label1.get_text()
        return Gtk.ContentProvider.new_for_value(text)

    # Получение данных при перетаскивании
    def on_drop(self, drop_target, value, x, y):
        text = value  # Прямое использование значения
        self.label2.set_text(text)
        return True

class DragDropApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.example.dragdrop")
    
    def do_activate(self):
        window = DragDropExample(self)
        window.present()

# Запуск приложения
app = DragDropApp()
app.run()

