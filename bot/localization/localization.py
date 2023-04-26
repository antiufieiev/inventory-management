from enum import Enum


class Language(Enum):
    RU = 1
    UA = 2


class Keys(Enum):
    SELECT_USER = 1
    ADD_USER_SUCCESS = 2
    ACCESS_LEVEL_ADMIN = 3
    ACCESS_LEVEL_EMPLOYEE = 4
    ADMIN = 5
    EMPLOYEE = 6
    SELECT_ACCESS_LEVEL = 7
    ERROR_BLANK_USERNAME = 8
    ENTER_CHEESE_NAME = 9
    ERROR_CHEESE_TYPE_EXIST = 10
    CHEESE_TYPE_ADDED = 11
    ERROR_EMPTY = 12
    SELECT_CHEESE_TYPE = 13
    ENTER_CHEESE_AMOUNT = 14
    ENTER_CHEESE_PACKED_STATE = 15
    ERROR_NO_TYPE_EXIST = 16
    CHEESE_PACKED = 17
    CHEESE_UNPACKED = 18
    CHEESE_PACKED_STATE = 19
    ERROR_ADD_USER = 20
    ADD_CHEESE_SUCCESS = 21
    ERROR_BATCH_INSERT = 22
    ERROR_LOG_INSERT = 23
    COMMAND_LOG_SUCCESS = 24
    ENTER_CHEESE_BATCH = 25
    SELECT_CHEESE_BATCH = 26
    CHOOSE_USER = 27
    PRINT_LOG = 28
    PRINT_DATABASE_STATE = 29
    CHEESE_DELETE_SUCCESS = 30
    USE_KEYBOARD_AS_INPUT_ERROR = 31
    ACCESS_DENIED = 32
    ENTER_COMMENT = 33
    COUNT_INPUT_ERROR_NUMERIC = 34
    COUNT_INPUT_ERROR_OVERLOAD = 35
    PRINT_DATABASE_STATE_LINE = 36
    USER_DELETED = 37
    ENTER_PACKAGING = 38
    ACCESS_LEVEL_MANAGER = 39
    EMPLOYEE_ADD_CHEESE_SUCCESS = 40,
    ADD_CHEESE_SUCCESS_NO_PACKAGING = 40
    CHEESE_VARIANT_DELETED = 41


ru_map = {
    Keys.SELECT_USER: "Выберите пользователя",
    Keys.ACCESS_LEVEL_ADMIN: "Администратор",
    Keys.ACCESS_LEVEL_EMPLOYEE: "Сотрудник",
    Keys.ADMIN: "Администратор",
    Keys.EMPLOYEE: "Сотрудник",
    Keys.SELECT_ACCESS_LEVEL: "Выберите уровень доступа",
    Keys.ERROR_BLANK_USERNAME: "Некорректное имя пользователя",
    Keys.ADD_USER_SUCCESS: "Готово! Пользователю {0} был надан уровень доступа: {1}",
    Keys.ENTER_CHEESE_NAME: "Введите новый сорт сыра",
    Keys.CHEESE_TYPE_ADDED: "Готово! Новый сорт сыра с названием {0} был успешно добавлен",
    Keys.ERROR_CHEESE_TYPE_EXIST: "Ошибка! Данный вид сыра уже существует",
    Keys.ERROR_EMPTY: "Ошибка! Ввод пустой",
    Keys.SELECT_CHEESE_TYPE: "Выберите сорт сыра",
    Keys.ENTER_CHEESE_AMOUNT: "Введите количество",
    Keys.ENTER_CHEESE_PACKED_STATE: "Введите состояние",
    Keys.ERROR_NO_TYPE_EXIST: "Сорт {0} не существует в базе",
    Keys.CHEESE_PACKED: "Упакован",
    Keys.CHEESE_UNPACKED: "Не упакован",
    Keys.CHEESE_PACKED_STATE: "Введите состояние",
    Keys.ERROR_ADD_USER: "Ошибка! Пользователь уже существует",
    Keys.ADD_CHEESE_SUCCESS: "Успех! Добавлена партия {0} в количестве {1}. Фасовка: {2}",
    Keys.ADD_CHEESE_SUCCESS_NO_PACKAGING: "Успех! Добавлена партия {0} в количестве {1}.",
    Keys.ERROR_BATCH_INSERT: "Ошибка! Партия уже существует! Попробуйте заново!",
    Keys.ERROR_LOG_INSERT: "Ошибка! Невозможно добавить пользователя и команду в логи!",
    Keys.COMMAND_LOG_SUCCESS: "Было выполнено действие: {0}.\nВ команде: {1}",
    Keys.ENTER_CHEESE_BATCH: "Выберите номер партии:",
    Keys.SELECT_CHEESE_BATCH: "Выберите партию:",
    Keys.CHOOSE_USER: "Выберите никнейм сотрудника:",
    Keys.PRINT_LOG: "userId: {0}\n{1}\nDate: {2}",
    Keys.PRINT_DATABASE_STATE_LINE: u"{0} \U0001F9C0{1}: {2} Комментарий: {3}\n",
    Keys.PRINT_DATABASE_STATE: "Запакованные: \n{0} \nНезапакованные: \n{1} ",
    Keys.CHEESE_DELETE_SUCCESS: "Успешно было удалено {0} штук сыра вида {1} с партии {2}",
    Keys.USE_KEYBOARD_AS_INPUT_ERROR: "Ошибка! Пожалуйста используйте клавиатуру для ввода корректного уровня доступа!",
    Keys.ACCESS_DENIED: "Ошибка! Вы не имеете доступа к этой команде!",
    Keys.ENTER_COMMENT: "Введите комментарий",
    Keys.COUNT_INPUT_ERROR_NUMERIC: "Ошибка! Ожидается число",
    Keys.COUNT_INPUT_ERROR_OVERLOAD: "Ошибка! В партии меньше сыра, чем введено. Введите корректное количество!",
    Keys.USER_DELETED: "Пользователь {0} успешно удален из системы.",
    Keys.ENTER_PACKAGING: "Введите фасовку",
    Keys.ACCESS_LEVEL_MANAGER: "Менеджер",
    Keys.EMPLOYEE_ADD_CHEESE_SUCCESS: "Готово! Добавлена партия {0} в количестве {1}. Не забудьте указать номер партии и повесить табличку.",
    Keys.CHEESE_VARIANT_DELETED: "Успех! Вид cыра с названием {0} удален из системы."
}

localization_map = ru_map
