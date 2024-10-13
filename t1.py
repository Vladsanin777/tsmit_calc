import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, GObject

class DragDropExample(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("Drag and Drop Example with Buttons")
        self.set_default_size(600, 200)

        # Контейнеры для перетаскивания
        self.box1 = Gtk.Box(spacing=0, orientation=Gtk.Orientation.VERTICAL)  # Убираем отступы
        self.box2 = Gtk.Box(spacing=0, orientation=Gtk.Orientation.VERTICAL)  # Убираем отступы

        # Создаем 5 ячеек (с кнопками) для дропа
        self.drop_cells = []
        for i in range(5):
            cell = Gtk.Box(spacing=0, orientation=Gtk.Orientation.VERTICAL)  # Убираем отступы
            cell.set_name(f"drop_cell_{i + 1}")  # Уникальное имя для ячейки
            self.drop_cells.append(cell)
            self.box2.append(cell)  # Добавляем ячейки в вертикальный контейнер

        # Добавляем контейнеры в основное окно
        main_box = Gtk.Box(spacing=0, orientation=Gtk.Orientation.HORIZONTAL)  # Убираем отступы
        self.set_child(main_box)
        main_box.append(self.box1)
        main_box.append(self.box2)

        # Добавляем кнопки в первый контейнер
        for i in range(3):
            label_button = Gtk.Label.new(f"Button {i + 1}")
            (button := Gtk.Button()).set_child(label_button)
            button.set_margin_start(0)  # Убираем внешние отступы
            button.set_margin_end(0)
            button.set_margin_top(0)
            button.set_margin_bottom(0)
            self.box1.append(button)

            # Настройка DragSource для каждой кнопки
            drag_source = Gtk.DragSource()
            drag_source.connect("prepare", self.on_drag_prepare)
            label_button.add_controller(drag_source)

        # Настройка DropTarget для каждой ячейки
        for cell in self.drop_cells:
            drop_target = Gtk.DropTarget.new(GObject.TYPE_STRING, Gdk.DragAction.COPY)
            drop_target.connect("drop", self.on_drop)
            cell.add_controller(drop_target)

        # Добавление стилей CSS
        self.add_css_styles()

    def add_css_styles(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data("""
            #drop_cell_1, #drop_cell_2, #drop_cell_3, #drop_cell_4, #drop_cell_5 {
                background-color: rgba(204, 204, 204, 1); /* Светло-серый фон */
                border: 2px dashed rgba(150, 150, 150, 1); /* Дашированный бордер */
                margin: 0;  /* Убираем внешние отступы */
            }
            #drop_cell_1:hover, #drop_cell_2:hover, #drop_cell_3:hover, #drop_cell_4:hover, #drop_cell_5:hover {
                background-color: rgba(180, 180, 180, 1); /* Темнее при наведении */
            }
        """.encode('utf-8'))  # Кодируем в UTF-8 для передачи
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

    # Подготовка данных для перетаскивания (отправляем имя кнопки)
    def on_drag_prepare(self, drag_source, x, y):
        label = drag_source.get_widget()  # Получаем кнопку, с которой начинается DnD
        return Gdk.ContentProvider.new_for_value(label.get_text())  # Возвращаем уникальное имя кнопки как данные

    # Обработка получения кнопки в ячейке
    def on_drop(self, drop_target, name, x, y):
        # Определяем, к какой ячейке произошло перетаскивание
        cell = drop_target.get_widget()  # Получаем ячейку, в которую дропнули
        
        # Если в ячейке уже есть кнопка, удаляем её
        current_button = cell.get_first_child()  # Получаем первую (и единственную) кнопку
        if current_button is not None:
            cell.remove(current_button)  # Удаляем существующую кнопку

        # Создаем новую кнопку с тем же именем и добавляем в целевую ячейку
        new_button = Gtk.Button(label=name)
        new_button.set_name(name)  # Устанавливаем имя новой кнопки
        new_button.set_margin_start(0)  # Убираем отступы у кнопки
        new_button.set_margin_end(0)
        new_button.set_margin_top(0)
        new_button.set_margin_bottom(0)
        cell.append(new_button)  # Добавляем кнопку в целевую ячейку
        
        return True

class DragDropApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.example.dragdrop.buttons")
    
    def do_activate(self):
        window = DragDropExample(self)
        window.present()

# Запуск приложения
app = DragDropApp()
app.run()

