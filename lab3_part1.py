import tkinter as tk

RADIUS = 22          # постоянный радиус всех кругов

# Класс круга. Вся логика (попадание точки, отрисовка) - внутри объекта,
# координаты наружу не отдаются (инкапсуляция не нарушена).

class CCircle:
    def __init__(self, x, y):
        self._x = x
        self._y = y
        self._r = RADIUS
        self._selected = False
        self._canvas_id = None

    def is_point_inside(self, x, y):
        """Объект сам решает, попала ли в него мышка."""
        return (x - self._x) ** 2 + (y - self._y) ** 2 <= self._r ** 2

    def set_selected(self, flag):
        self._selected = bool(flag)

    def is_selected(self):
        return self._selected

    def draw(self, canvas):
        """Объект сам себя рисует на канве."""
        if self._canvas_id is not None:
            canvas.delete(self._canvas_id)          # стереть прошлую картинку
        if self._selected:
            outline, width, fill = "#c0392b", 3, "#f5b7b1"
        else:
            outline, width, fill = "#2c3e50", 1, "#d6eaf8"
        self._canvas_id = canvas.create_oval(
            self._x - self._r, self._y - self._r,
            self._x + self._r, self._y + self._r,
            outline=outline, width=width, fill=fill)

# Собственный контейнер. Снаружи ведёт себя как массив,
# внутри хранит объекты в ПРИВАТНОМ списке.

class CircleStorage:
    def __init__(self):
        self.__items = []                 # приватное хранилище

    def add(self, obj):
        self.__items.append(obj)

    def get_count(self):
        return len(self.__items)

    def get_object(self, index):
        return self.__items[index]

    def remove_at(self, index):
        del self.__items[index]


# Форма

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ЛР3 ч.1 - Круги на форме")
        self.geometry("800x600")

        self.storage = CircleStorage()

        hint = tk.Label(
            self,
            text="ЛКМ по пустому месту - новый круг | ЛКМ по кругу - выделить | "
                 "Ctrl(Cmd) + ЛКМ - выделить несколько | Delete - удалить выделенные",
            anchor="w", bg="#eeeeee")
        hint.pack(side=tk.TOP, fill=tk.X)

        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # мышь
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<Control-Button-1>", self.on_mouse_down)
        try:                                 
            self.canvas.bind("<Command-Button-1>", self.on_mouse_down)
        except tk.TclError:
            pass

        # изменение размера формы
        self.canvas.bind("<Configure>", self.on_resize)

        # Del
        self.bind("<Delete>", self.on_delete)
        self.bind("<BackSpace>", self.on_delete)

        self.canvas.focus_set()

    # ---------------- мышь ----------------
    def on_mouse_down(self, event):
        multi = bool(event.state & (0x0004 | 0x0008 | 0x0010))

        # ищем верхний (последний нарисованный) круг под курсором
        hit = None
        for i in range(self.storage.get_count() - 1, -1, -1):
            obj = self.storage.get_object(i)
            if obj.is_point_inside(event.x, event.y):
                hit = obj
                break

        if hit is None:
            # клик по пустому месту: создаём круг (и снимаем выделение,
            # если не была зажата клавиша множественного выбора)
            if not multi:
                self.clear_selection()
            self.storage.add(CCircle(event.x, event.y))
        else:
            if multi:
                hit.set_selected(not hit.is_selected())   # добавить/убрать
            else:
                self.clear_selection()
                hit.set_selected(True)                    # выделить только его
        self.redraw_all()

    def clear_selection(self):
        for i in range(self.storage.get_count()):
            self.storage.get_object(i).set_selected(False)

    # ---------------- клавиатура ----------------
    def on_delete(self, event=None):
        i = self.storage.get_count() - 1
        while i >= 0:
            if self.storage.get_object(i).is_selected():
                self.storage.remove_at(i)
            i -= 1
        self.redraw_all()

    # ---------------- отрисовка ----------------
    def on_resize(self, event):
        # форма поменяла размер - перерисовываем всё содержимое контейнера
        self.redraw_all()

    def redraw_all(self):
        self.canvas.delete("all")
        for i in range(self.storage.get_count()):
            self.storage.get_object(i).draw(self.canvas)


if __name__ == "__main__":
    App().mainloop()
