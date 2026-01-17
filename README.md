# Mine Language
![](image-url)
graph TD
    A[Исходный код .mc] --> B[Предобработка]
    B --> C[Лексический анализ]
    C --> D[Семантический анализ]
    D --> E[Генерация команд]
    E --> F[Создание датапака]
    F --> G[Готовые .mcfunction файлы]
    
    H[Моды .mh] --> B
    I[Базовые токены] --> C
    J[Пользовательские токены] --> C
## Обзор
Этот проект представляет собой **компилятор**, который *преобразует пользовательский скриптовый язык в функциональные датапаки для Minecraft*. Компилятор написан на *Python* и позволяет создавать сложные механики с помощью простого синтаксиса.

## Структура проекта
### Основные компоненты
Токенизатор **(Lexer)** - преобразует исходный код в последовательность токенов

*Парсер* **(Parser)** - анализирует токены для создания структуры данных

*Модульная система* **(ModsHandler)** - обеспечивает расширяемость через моды

*Генератор кода* **(Export)** - создает .mcfunction файлы

*Рабочее окружение* **(workspace)** - управляет созданием датапаков

## Как работает компилятор
### Процесс компиляции:

``` python
# Основной поток выполнения
1. Чтение исходного кода
2. Предобработка (удаление лишних пробелов, загрузка модов)
3. Лексический анализ (разбиение на токены)
4. Семантический анализ (проверка типов, значений)
5. Генерация Minecraft команд
6. Создание структуры датапака
7. Запись функций
```

### Токены
Система использует токены для представления различных элементов языка:

| Токен	| Описание	| Пример |
|:---------|:---------|:---------|
| <fn>	| Объявление функции	| fn main
| <end>	| Конец функции |	end
| <ex>	| Вызов функции |	execute function
| <int>	| Целое число |	42
| <string>	| Строка |	"Hello"
| <word>	| Идентификатор |	myVariable

# Скриптинг
## Базовый синтаксис
### Объявление функции:
``` text
fn main
  output "Hello...World"
end
```
### Создание переменных:
```text
create <string> message
mode message value "Hello Minecraft"

create <int> counter
mode counter value 10

create <array> positions
mode positions vec3 10 20 30
```
### Вывод данных:
``` text
output "Simple text"
output message value
output <string> "Counter...value:" counter value
```
### Выполнение функций:
```text
execute other_function
```
## Пример скрипта script.mc:
```text
pack scripts/studio.mh
pack scripts/mod.mh

fn setup
  create <string> welcome
  mode welcome value "Welcome...to...our...server!"
  
  output welcome value
end

fn main
  create <int> timer
  mode timer value 0
  
  cycle 1
  
  output <string> "Current...time:" timer value
end
```

# Моддинг
## Структура мода
**Мод** - это *Python-класс*, который расширяет возможности компилятора:

``` python
class YourMod:
    LocTokens = [
        ['ключевое_слово', '<токен>'],
        ['другое_слово', '<другой.токен>']
    ]
    
    def LocalAnoncement(values, tokens_line, extokens):
        # Обработка объявлений и модификаций
        return extokens
    
    def TranslatedFunctions(tokens_line, excode, values):
        # Генерация Minecraft команд
        return excode
```
## Создание нового типа данных
```python
class CustomMod:
    LocTokens = [
        ['create_block', '<create.block>'],
        ['place', '<place>']
    ]
    
    def LocalAnoncement(values, tokens_line, extokens):
        # Определяем новый тип - блок
        type BlockType = Callable[[None], dict[str]]
        Block: BlockType = lambda: {"type": "stone", "position": [0, 0, 0]}
        
        if locwork.verifTokenQueue(tokens_line, 'create.block', 'word'):
            _, block_name = locwork.getTokenValues(tokens_line[1])
            values[block_name] = Block()
        
        return extokens
    
    def TranslatedFunctions(tokens_line, excode, values):
        # Генерация команды установки блока
        if locwork.verifTokenQueue(tokens_line, 'place', 'word', 'int', 'int', 'int'):
            _, block = locwork.getTokenValues(tokens_line[1])
            _, x = locwork.getTokenValues(tokens_line[2])
            _, y = locwork.getTokenValues(tokens_line[3])
            _, z = locwork.getTokenValues(tokens_line[4])
            
            excode += f'setblock {x} {y} {z} {values[block]["type"]}'
        
        return excode
```
## Регистрация мода
Моды загружаются с помощью директивы pack:

``` text
pack path/to/your/mod.mh
```

# Базовая библиотека (Studio)
*Встроенная библиотека* предоставляет основные функции:

## Типы данных:
- **<string>** - строковый тип

- **<int>** - целочисленный тип

- **<array>** - массив значений

- **vec3** - трехмерный вектор

## Команды:
- **create** - создание переменной

- **mode** - изменение значения

- **output** - вывод в чат

# Установка и использование
## Требования:
- **Python 3.6+**
- **Minecraft с поддержкой датапаков**

## Запуск:
``` bash
python main.py путь/к/скрипту.mc путь/к/миру
```
## Пример:

``` bash
python main.py scripts/script.mc "C:\Users\username\AppData\Roaming\.minecraft\saves\World"
```
## Структура генерируемого датапака
```text
world/datapacks/script/
├── pack.mcmeta
├── data/
│   ├── minecraft/
│   │   └── tags/
│   │       └── functions/
│   │           ├── load.json
│   │           └── tick.json
│   └── script/
│       └── functions/
│           ├── main.mcfunction
│           ├── setup.mcfunction
│           └── другие_функции.mcfunction
```
## Расширенные возможности
### Работа с массивами:
```text
create <array> points
mode points vec3 0 64 0
mode points vec3 10 64 5
mode points vec3 20 64 10
```
### Пользовательские моды:
Создайте файл **.mh** с вашим модом и подключите его через pack директиву.

### Отладка
Компилятор предоставляет информацию о процессе:
- Выводит создаваемые пути
- Показывает загруженные моды
- Отображает локальные значения переменных

### Ограничения
1. Язык чувствителен к регистру
2. Требуется строгое соблюдение синтаксиса
3. Все функции должны быть явно объявлены и закрыты
4. Переменные имеют локальную область видимости

### Примеры модов
#### Мод для телепортации:
``` python
class TeleportMod:
    LocTokens = [
        ['teleport', '<tp>'],
        ['to', '<to>']
    ]
    
    def TranslatedFunctions(tokens_line, excode, values):
        if locwork.verifTokenQueue(tokens_line, 'tp', 'word', 'to', 'word'):
            _, entity = locwork.getTokenValues(tokens_line[1])
            _, destination = locwork.getTokenValues(tokens_line[3])
            excode += f'tp {entity} {destination}'
        return excode
```
#### Использование в скрипте:

```text
teleport @p to spawn_point
```
# Заключение
Этот компилятор предоставляет *мощный *и* расширяемый* способ создания сложных механик для Minecraft через простой скриптовый язык. Модульная архитектура позволяет легко добавлять новые возможности, делая его идеальным инструментом для создания кастомных датапаков.
