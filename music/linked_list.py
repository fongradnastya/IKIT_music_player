"""
Реализация кольцевого двусвязного списка
"""


class LinkedListItem:
    """
    Класс элемента Linked List
    """

    def __init__(self, item):
        """
        Создаёт новый элемент двусвязного списка
        :param item: значение для текущего элемента
        """
        self._next_item = None
        self._previous_item = None
        self._item = item

    @property
    def next_item(self):
        """Getter для следующего элемента"""
        return self._next_item

    @property
    def previous_item(self):
        """
        Getter для предыдущего элемента
        """
        return self._previous_item

    @next_item.setter
    def next_item(self, value):
        """
        Setter для следующего элемента
        :param value: значение для следующего элемента списка
        :return:
        """
        if value:
            if self._next_item != value:
                self._next_item = value
                value.previous_item = self
        else:
            self._next_item = None

    @previous_item.setter
    def previous_item(self, value):
        """Setter для следующего элемента"""
        if value:
            if self._previous_item != value:
                self._previous_item = value
                value.next_item = self
        else:
            self._previous_item = None

    @property
    def item(self):
        """Возврат элемента"""
        return self._item


class LinkedList:
    """
    Класс реализации кольцевого двусвязного списка
    """

    def __init__(self, item=None):
        """
        Создаёт экземпляр класса
        :param item: первый элемент списка
        """
        self.head = None
        self.count_item = 0
        if item:
            self.append(item)

    @property
    def first_item(self):
        """Возвращает последний элемент"""
        return self.head

    @property
    def last(self):
        """Возвращает последний элемент"""
        result = None
        if self.head:
            result = self.head.previous_item
        return result

    def append_left(self, item: LinkedListItem):
        """
        Добавление элемента в начало списка
        :param item: элемент для добавления
        :return:
        """
        if not isinstance(item, LinkedListItem):
            item = LinkedListItem(item)
        if not self.head:
            self.head = item
            self.head.next_item = self.head
            self.head.previous_item = self.head
        else:
            self.head.previous_item.next_item = item
            item.next_item = self.head
            self.head = self.head.previous_item

    def append_right(self, item: LinkedListItem):
        """
        Добавление элемента в конец списка
        :param item: значение для добавления
        :return:
        """
        if not isinstance(item, LinkedListItem):
            item = LinkedListItem(item)
        if not self.head:
            self.head = item
            if self.head.next_item:
                current = self.head
                while current.next_item != self.head:
                    current = current.next_item
                self.head.previous_item = current
                current.next_item = self.head
            else:
                self.head.previous_item = self.head
        else:
            self.head.previous_item.next_item = item
            item.next_item = self.head

    def append(self, item: LinkedListItem):
        """
        Аналог метода append_right
        :param item: значение для добавления
        :return:
        """
        self.append_right(item)

    def remove(self, item: LinkedListItem):
        """
        Удаление элемента по значению
        :param item: значение удаляемого элемента
        :return:
        """
        if not isinstance(item, LinkedListItem):
            item = LinkedListItem(item)
        if self.head:
            if item.item == self.head.item:
                if self.head.next_item == self.head:
                    self.head = None
                else:
                    remove_item = self.head
                    self.head = self.head.next_item
                    remove_item.next_item.previous_item = \
                        remove_item.previous_item
                    remove_item.next_item = None
                    remove_item.previous_item = None
            else:
                current = self.head.next_item
                error = True
                while current != self.head:
                    if current.item == item.item:
                        error = False
                        break
                    current = current.next_item

                if not error:
                    remove_item = current
                    remove_item.next_item.previous_item = \
                        remove_item.previous_item
                    remove_item.next_item = None
                    remove_item.previous_item = None
                else:
                    raise ValueError("There are no elements with such value")
        else:
            raise ValueError("Nothing to delete")

    def insert(self, previous, item):
        """
        Вставка элемента item после элемента previous
        :param previous: предыдущее значение LinkedListItem
        :param item: значение элемента для вставки
        :return:
        """
        if self.head:
            if not isinstance(item, LinkedListItem):
                item = LinkedListItem(item)
            if self.head == previous:
                self.head.next_item.previous_item = item
                self.head.next_item = item
            else:
                current = self.head
                while current.previous_item != previous:
                    current = current.previous_item
                current.previous_item.next_item = item
                current.previous_item = item
        else:
            raise ValueError("There is no previous element")

    def __len__(self):
        """Возврат длины списка"""
        length = 0
        if self.head:
            length += 1
            current = self.head
            while current.next_item != self.head:
                length += 1
                current = current.next_item

        return length

    def __iter__(self):
        """Возврат итератора"""
        self.count_item = 0
        return self

    def __next__(self):
        """Возврат следующего элемента"""
        if self.count_item == len(self):
            raise StopIteration()

        return_item = self[self.count_item]
        self.count_item += 1

        return return_item

    def __getitem__(self, index):
        """
        Возврат элемента по индексу
        :param index: индекс возвращаемого элемента
        :return:
        """
        if not self.head:
            raise IndexError()
        if index >= len(self):
            raise IndexError("Index is too big")

        if index < 0:
            index = index + len(self)
            if index < 0:
                raise IndexError("Index can't be negative")
            result = self[index]
        if not 0 <= index < len(self):
            raise IndexError("Index out of range")
        i = 0
        current = self.head
        while i != index:
            i += 1
            current = current.next_item
        result = current
        return result

    def __contains__(self, item):
        """
        Поддержка оператора in
        :param item: значение для проверки на вхождение
        :return:
        """
        in_linked_list = False
        if self.head:
            for linked_list_item in enumerate(self):
                if linked_list_item[1].item == item:
                    in_linked_list = True
                    break

        return in_linked_list

    def __reversed__(self):
        """Поддержка функции reversed"""
        result = self
        if self.head:
            new_head = LinkedList()
            current = self.head.previous_item
            new_head.append(current.item)
            current = current.previous_item
            while current != self.head.previous_item:
                new_head.append(current.item)
                current = current.previous_item
            result = new_head
        return result
