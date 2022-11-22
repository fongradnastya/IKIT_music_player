"""
Модуль, реализующий двусвязный списком
"""


class LinkedListItem:
    """Узел связного списка"""
    def __init__(self, data=None) -> None:
        """Инициализация узла связного списка"""
        self.data = data
        self._previous = None
        self._next = None

    @property
    def next_item(self) -> "LinkedListItem":
        """Получение следующего элемент"""
        return self._next

    @next_item.setter
    def next_item(self, value: "LinkedListItem") -> None:
        """Установка следующего элемента"""
        if value is not None:
            if self.next_item != value:
                self._next = value
                value.previous_item = self
        else:
            self._next = None

    @property
    def previous_item(self) -> "LinkedListItem":
        """Получение предыдущего элемента"""
        return self._previous

    @previous_item.setter
    def previous_item(self, value: "LinkedListItem") -> None:
        """Установка предыдущего элемента"""

        # Проверяем, что значение передано
        if value is not None:
            # Если предыдущий элемент не равен текущему
            if self.previous_item != value:
                self._previous = value
                value.next_item = self
        else:
            self._previous = None

    def __repr__(self) -> str:
        """Читаемое отображение узла связного списка"""
        return str(self.data)


class LinkedList:
    """Двусвязный список"""

    def __init__(self, first_item=None) -> None:
        """Инициализация кольцевого двусвязного списка"""
        self.first_item = None
        self.items_count = 0
        if first_item:
            self.append(first_item)

    @property
    def last(self) -> None:
        """Последний элемент"""
        if self.first_item:
            return self.first_item.previous_item
        return None

    def append_left(self, item: object) -> None:
        """Добавление элемента в начало списка"""
        if not isinstance(item, LinkedListItem):
            item = LinkedListItem(item)
        if not self.first_item:
            self.first_item = item
            self.first_item.next_item = self.first_item
            self.first_item.previous_item = self.first_item
        else:
            self.first_item.previous_item.next_item = item
            item.next_item = self.first_item
            self.first_item = item

    def append_right(self, item: object) -> None:
        """Добавление элемента в конец списка"""
        if not isinstance(item, LinkedListItem):
            item = LinkedListItem(item)
        if not self.first_item:
            self.first_item = item
            if self.first_item.next_item:
                current_item = self.first_item
                while current_item.next_item != self.first_item:
                    current_item = current_item.next_item
                self.first_item.previous_item = current_item
            else:
                self.first_item.previous_item = self.first_item
        else:
            self.last.next_item = item
            self.first_item.previous_item = item

    def append(self, item: object) -> None:
        """Добавление справа"""
        self.append_right(item)

    def remove(self, item: int) -> None:
        """Удаление элемента"""
        item = LinkedListItem(item)
        if not self.first_item:
            raise ValueError("This list is empyty")
        if item.data == self.first_item.data:
            if self.last == self.first_item:
                self.first_item = None
            else:
                remove_item = self.first_item
                self.first_item = self.first_item.next_item
                remove_item.next_item.previous_item = remove_item.previous_item
                remove_item.next_item = None
                remove_item.previous_item = None
        else:
            current_item = self.first_item.next_item
            desired_element = True
            while current_item != self.first_item:
                if current_item.data == item.data:
                    desired_element = False
                    break
                current_item = current_item.next_item
            if desired_element is False:
                remove_item = current_item
                remove_item.next_item.previous_item = remove_item.previous_item
                remove_item.next_item = None
                remove_item.previous_item = None
            else:
                raise ValueError("No suitable elements to delete")

    def insert(self, previous: LinkedListItem, item: int):
        """Вставка справа"""
        if not isinstance(previous, LinkedListItem):
            raise ValueError("Previous is not instance LinkedListItem")
        if not isinstance(item, LinkedListItem):
            item = LinkedListItem(item)
        if self.first_item:
            if self.last == self.first_item:
                self.last.previous_item = item
                item.previous_item = self.first_item
            else:
                current_item = self.first_item
                while current_item.previous_item != previous:
                    current_item = current_item.previous_item
                current_item.previous_item.next_item = item
                item.next_item = current_item
        else:
            raise ValueError("Incorrect value of previous item. Impossible to"
                             " add")

    def __len__(self):
        """Длина списка"""
        length = 0
        if self.first_item:
            length += 1
            current_item = self.first_item
            while current_item.next_item != self.first_item:
                length += 1
                current_item = current_item.next_item
        return length

    def __iter__(self):
        """Получение итератора"""
        new_item = self.first_item
        while new_item:
            if new_item.next_item != self.first_item:
                yield new_item
                new_item = new_item.next_item
            else:
                yield new_item
                break

    def __getitem__(self, index: int) -> "LinkedListItem":
        """Получение элемента по индексу"""
        if not self.first_item:
            raise IndexError("This list is empty")
        elif index >= len(self):
            raise IndexError("Positive index out of range")
        elif index < 0:
            index += len(self)
            if index < 0:
                raise IndexError("Negative index out of range")
        elif not isinstance(index, int):
            raise IndexError("Index must be integer")
        current_item = self.first_item
        for i in range(index):
            current_item = current_item.next_item
        return current_item

    def __contains__(self, item: "LinkedListItem") -> bool:
        """Поддержка оператора in"""
        if self.first_item is None:
            return False
        new_item = self.first_item
        while new_item.next_item != self.first_item:
            if new_item.data == item:
                return True
            else:
                new_item = new_item.next_item
        if new_item.data == item:
            return True
        return False

    def __reversed__(self) -> None:
        """Поддержка функции reversed"""
        new_item = self.last
        while new_item:
            if new_item.previous_item != self.last:
                yield new_item
                new_item = new_item.previous_item
            else:
                yield new_item
                break

    def __repr__(self) -> str:
        """
        Создаёт строковое представление объекта
        :return: строковое представление
        """
        if not self.first_item:
            return "LinkedList[]"
        string = "LinkedList["
        for item in self:
            string = f"{string}{item}, "
        string = string[:-2] + "]"
        return string

    def __str__(self) -> str:
        """
        Создаёт строковое представление объекта
        :return: строковое представление
        """
        return self.__repr__()
