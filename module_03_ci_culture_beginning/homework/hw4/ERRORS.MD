# ERRORS.MD

## Класс Person и его методы

В этом файле описаны ошибки, допущенные в методах класса `Person`, и объясняется, как их правильно исправлять.

Исходный код:

```python
import datetime


class Person:
    def __init__(self, name: str, year_of_birth: int, address: str = '') -> None:
        self.name: str = name
        self.yob: int = year_of_birth
        self.address: str = address

    def get_age(self) -> int:
        now: datetime.datetime = datetime.datetime.now()
        # корректно: текущий год минус год рождения
        return now.year - self.yob

    def get_name(self) -> str:
        return self.name

    def set_name(self, name: str) -> None:
        # должно присваивать новое имя, а не само себе
        self.name = name

    def set_address(self, address: str) -> None:
        # должно присваивать новое значение, а не сравнивать
        self.address = address

    def get_address(self) -> str:
        return self.address

    def is_homeless(self) -> bool:
        """
        returns True if address is not set, false in other case
        """
        return self.address == '' or self.address is None
```

---

## Ошибка 1: set_name

### Описание ошибки

Комментарий в методе `set_name` явно указывает на типичную ошибку:

```python
def set_name(self, name: str) -> None:
    # должно присваивать новое имя, а не само себе
    self.name = name
```

Изначально метод мог быть реализован неверно, например:

```python
def set_name(self, name: str) -> None:
    self.name = self.name  # имя не меняется, аргумент name игнорируется
```

В такой реализации поле `self.name` всегда остаётся прежним, и вызов `set_name("Новое имя")` никак не меняет объект.

### Правильная реализация

Метод должен присваивать атрибуту `self.name` значение аргумента `name`:

```python
def set_name(self, name: str) -> None:
    self.name = name
```

---

## Ошибка 2: set_address

### Описание ошибки

В методе `set_address` комментарий указывает на другую распространённую ошибку:

```python
def set_address(self, address: str) -> None:
    # должно присваивать новое значение, а не сравнивать
    self.address = address
```

Некорректный вариант мог выглядеть так:

```python
def set_address(self, address: str) -> None:
    self.address == address  # используется оператор сравнения, а не присваивание
```

Здесь оператор `==` просто сравнивает текущий адрес с новым, но не изменяет значение атрибута `self.address`. В результате метод ничего не делает.

### Правильная реализация

Метод должен записывать новое значение в поле `self.address`:

```python
def set_address(self, address: str) -> None:
    self.address = address
```

---

## Метод get_age

### Состояние

Метод `get_age` реализован логически корректно:

```python
def get_age(self) -> int:
    now: datetime.datetime = datetime.datetime.now()
    # корректно: текущий год минус год рождения
    return now.year - self.yob
```

Он вычисляет возраст как разницу между текущим годом и годом рождения. Такой подход соответствует комментарию и требованиям задачи (если не требуется учитывать точную дату рождения).

---

## Метод is_homeless

### Состояние

Метод `is_homeless` определяет, считается ли человек «без адреса»:

```python
def is_homeless(self) -> bool:
    """
    returns True if address is not set, false in other case
    """
    return self.address == '' or self.address is None
```

Он возвращает `True`, если адрес либо пустая строка, либо `None`. Это соответствует описанию в docstring («если адрес не установлен»). Явной логической ошибки в текущей реализации нет.

Если по условию задачи пустая строка должна считаться валидным адресом, то проверку нужно было бы сузить только до `None`. В рамках текущего задания комментарий и реализация совпадают.