from django.db import models
from django.urls import reverse


class Composition(models.Model):
    name = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.ImageField(upload_to="photos/%Y/%m/%d/")
    audio = models.FileField(upload_to="audio/%Y/%m/%d/")
    is_played = models.BooleanField(default=False)
    is_liked = models.BooleanField(default=False)

    order = models.PositiveSmallIntegerField(default=0, blank=True, null=True)

    def __str__(self):
        return f"{self.name}, {self.author}"

    def get_absolute_url(self):
        return reverse('post', kwargs={'post_id': self.pk})

    class Meta:
        ordering = ['name', 'author']


class LinkedList:
    """
    Класс реализации кольцевого двусвязного списка
    """

    def __init__(self, item=None):
        self.head = None
        self.count_item = 0
        if item:
            self.append(item)

    @property
    def first_item(self):
        """Возвращает последний элемент"""
        return self.head

    @property
    def last_item(self):
        """Возвращает последний элемент"""
        result = None
        if self.head:
            result = self.head.previous_item
        return result

    def append_left(self, item):
        """Добавление элемента в начало списка"""
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

    def append_right(self, item):
        """Добавление элемента в конец списка"""
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

    def append(self, item):
        """Добавление элемента в конец списка"""
        self.append_right(item)

    def remove(self, item):
        """Удаление элемента"""
        if not isinstance(item, LinkedListItem):
            item = LinkedListItem(item)
        if self.head:
            if item.item == self.head.item:
                if self.head.next_item == self.head:
                    self.head = None
                else:
                    remove_item = self.head
                    self.head = self.head.next_item
                    remove_item.next_item.previous_item = remove_item.previous_item
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
                    remove_item.next_item.previous_item = remove_item.previous_item
                    remove_item.next_item = None
                    remove_item.previous_item = None
                else:
                    raise ValueError()
        else:
            raise ValueError()

    def insert(self, previous, item):
        """Вставка элемента item после элемента previous"""
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
            raise ValueError()

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
        """Возврат элемента по индексу"""
        if not self.head:
            raise IndexError()
        if index >= len(self):
            raise IndexError()

        if index < 0:
            index = index + len(self)
            if index < 0:
                raise IndexError()
            result = self[index]
        if not 0 <= index < len(self):
            raise IndexError()
        i = 0
        current = self.head
        while i != index:
            i += 1
            current = current.next_item
        result = current
        return result

    def __contains__(self, item):
        """Поддержка оператора in"""
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


class Playlist(models.Model):
    name = models.CharField(max_length=255, null=True)
    cover = models.ImageField(upload_to="photos/%Y/%m/%d/",
                              default="photos/2022/11/07/cover.png")
    description = models.CharField(max_length=500, null=True, blank=True)
    is_default = models.BooleanField(default=False)
    compositions = models.ManyToManyField(Composition,
                                          through='PlaylistsCompositions')

    def __str__(self):
        return f"{self.name}"


class PlaylistsCompositions(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    composition = models.ForeignKey(Composition, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['order']
