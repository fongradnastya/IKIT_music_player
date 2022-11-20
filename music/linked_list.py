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

        # Проверяем, что значение передано
        if value is not None:
            # Если следующий элемент не равен текущему
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
        """Инициализация колльцевого двусвязного списка"""
        self.first_item = None

        # Для того чтобы переменная была видна во всех методах
        self.items_count = 0

        # Проверяем, что объект передан
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

        # Если первого элемента нет
        if not self.first_item:
            self.first_item = item
            self.first_item.next_item = self.first_item
            self.first_item.previous_item = self.first_item

        else:
            # Устанавливаем у последнего элемента списка следующий элемент вместо first_item
            self.first_item.previous_item.next_item = item

            # Новый элемент теперь стоит перед первым, first_item становится вторым элементом
            item.next_item = self.first_item

            # Меняем ссылку на первый элемент
            self.first_item = item

    def append_right(self, item: object) -> None:
        """Добавление элемента в конец списка"""
        if not isinstance(item, LinkedListItem):
            item = LinkedListItem(item)

        # Если первого элемента нет
        if not self.first_item:
            self.first_item = item

            # Если ссылка на следующий элемент не пустая
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

        # Если первого элемента нет
        if not self.first_item:
            raise ValueError()

            # Если мы хотим удалить первый элемент
        if item.data == self.first_item.data:

            # Проверка, что в списке всего 1 элемент
            if self.last == self.first_item:
                # "Обнуляем ссылку на первый элемент"
                self.first_item = None

            else:
                remove_item = self.first_item
                self.first_item = self.first_item.next_item
                remove_item.next_item.previous_item = remove_item.previous_item

                # Убираем у удалённого элемента ссылки на следующий и предыдущий элемент.
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
                raise ValueError()

    def insert(self, previous: "LinkedListItem", item: int):
        """Вставка справа"""

        if not isinstance(previous, LinkedListItem):
            raise ValueError("previous должен быть элементом связного списка.")

        if not isinstance(item, LinkedListItem):
            item = LinkedListItem(item)

        # Если первый элемент есть
        if self.first_item:

            # Сравнение позволяет понять, что у нас один элемент в списке
            if self.last == self.first_item:
                # Устанавливаем следующий элемент
                self.last.previous_item = item
                item.previous_item = self.first_item

            else:
                current_item = self.first_item
                while current_item.previous_item != previous:
                    current_item = current_item.previous_item
                current_item.previous_item.next_item = item
                item.next_item = current_item
        else:
            # Чтобы пройти test_insert FAILED
            raise ValueError()

    def __len__(self):
        """Длина списка"""
        length = 0

        # Если первый элемент есть
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

        while new_item:  # Если есть элемент
            if new_item.next_item != self.first_item:
                yield new_item  # "Выкидываемое" значение
                new_item = new_item.next_item  # Переход к следующему элементу
            else:
                yield new_item
                break

    def __getitem__(self, index):
        """Получение элемента по индексу"""

        # Если элементом нет
        if not self.first_item:
            raise IndexError()

        elif index >= len(self):
            raise IndexError()

        elif index < 0:
            index += len(self)
            if index < 0:
                raise IndexError()

        elif not isinstance(index, int):
            raise IndexError()

        current_item = self.first_item

        for _ in range(index):
            current_item = current_item.next_item

        return current_item

    def __contains__(self, item):
        """Поддержка оператора in"""

        if self.first_item is None:
            return False

        new_item = self.first_item

        while new_item.next_item != self.first_item:
            if new_item.data == item:
                return True
            else:
                new_item = new_item.next_item  # Переход к следующему элементу

        if new_item.data == item:
            return True
        return False

    def __reversed__(self):
        """Поддержка функции reversed"""

        new_item = self.last

        while new_item:  # Если есть элемент
            if new_item.previous_item != self.last:
                yield new_item  # "Выкидываемое" значение
                new_item = new_item.previous_item  # Переход к следующему элементу
            else:
                yield new_item
                break

    def __repr__(self):
        return str([item for item in self])