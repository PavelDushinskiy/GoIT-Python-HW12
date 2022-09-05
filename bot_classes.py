import datetime
from collections import UserDict
import re
import pickle
from bot_decorators import command_handler, parser_handler

RECORDS_PER_PAGE = 30

commands = {
    "hello",
    "add",
    "change",
    "phone",
    "show all",
    "good bye",
    "close",
    "exit",
    "find",
}


def _now():
    return datetime.datetime.today()


class Field:
    def __init__(self, value):
        self._value = None
        self.value = value

    def __repr__(self):
        return self.value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class Name(Field):
    def __init(self, ):
        pass


class Phone(Field):
    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value):
        self._value = f"Redefined: {value}"


class Birthday(Field):
    @property
    def value(self) -> datetime.datetime.date:
        return self._value

    @value.setter
    def value(self, value):
        self._value = datetime.datetime.strptime(value, "%d.%m.%Y")

    def __repr__(self):
        return datetime.datetime.strftime(self._value, "%d.%m.%Y")


class Record:
    def __init__(self, name: Name, phone: Phone = None, birthday: Birthday = None):
        self.name: Name = name
        self.phones: list[Phone] = [phone] if phone is not None else []
        self.birthday = birthday

    def add_phone(self, phone: Phone):
        self.phones.append(phone)

    def change_phone(self, old_phone: Phone, new_phone: Phone):
        try:
            self.phones.remove(old_phone)
            self.phones.append(new_phone)
        except ValueError:
            return f"{old_phone} does not exist"

    def find_phone(self, to_find: str):
        for phone in self.phones:
            if phone.value == to_find:
                return phone
        return None

    def delete_phone(self, phone: Phone):
        try:
            self.phones.remove(phone)
        except ValueError:
            return f"{phone} does not exist"

    def match_pattern(self, pattern):
        if re.search(pattern, self.name.value):
            return True
        for phone in self.phones:
            if re.search(pattern, phone.value):
                return True
        return False

    def days_to_birthday(self):
        now = _now().date()
        if self.birthday is not None:
            birthday: datetime.datetime.date = self.birthday.value.date()
            m_birthday = datetime.date(year=now.year, month=birthday.month, day=birthday.day)
            if m_birthday < now:
                m_birthday = m_birthday.replace(year=now.year + 1)
                return abs(m_birthday - now).days
        return None

    def __repr__(self):
        return f"{self.name.value} has numbers: {' '.join(phone.value for phone in self.phones)}"


class AddressBook(UserDict):
    __book_name = "address_book.bin"
    __items_per_page = 20

    def __enter__(self):
        self.__restore()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__save()

    def items_per_page(self, value):
        self.__items_per_page = value

    items_per_page = property(fget=None, fset=items_per_page)

    def __restore(self):
        try:
            with open(self.__book_name, "rb+") as file:
                book = pickle.load(file)
                self.data.update(book)
        except Exception:
            print("Book is not restored!")
            raise

    def __save(self):
        try:
            with open(self.__book_name, "wb+") as file:
                pickle.dump(self.data, file, protocol=pickle.HIGHEST_PROTOCOL)
                print("Book saved!")
        except Exception:
            print("Some problems!")
            raise

    def __iter__(self):
        self.page = 0
        return self

    def __next__(self):
        records = list(self.data.items())
        start_index = self.page * self.__items_per_page
        end_index = (self.page + 1) * self.__items_per_page
        self.page += 1
        if len(records) > end_index:
            to_return = records[start_index:end_index]
        else:
            if len(records) > start_index:
                to_return = records[start_index: len(records)]
            else:
                to_return = records[:-1]
        self.page += 1
        return [{record[1]: record[0]} for record in to_return]

    def add_contact(self, name: Name, phone: Phone = None):
        contact = Record(name=name, phone=phone)
        self.data[name.value] = contact

    def add_record(self, record: "Record"):
        self.data[record.name.value] = record

    def find_name(self, name: Name):
        try:
            return self.data[name]
        except KeyError:
            return None

    def find_phone(self, phone: Phone):
        for record in self.data.values():
            if phone in [number.value for number in record.phones]:
                return record
        return None

    def find_by_pattern(self, pattern):
        matched = []
        for record in self.data.values():
            if record.match_pattern(pattern):
                matched.append(record)
        return matched


class InputParser:
    @parser_handler
    def parse_user_input(self, user_input: str) -> tuple[str, list]:

        for command in commands:
            normalized_input = " ".join(
                list(filter(lambda x: x != "", user_input.lower().split(" ")))
            )
            normalized_input = normalized_input.ljust(len(normalized_input) + 1, " ")
            if normalized_input.startswith(command + " "):
                parser = getattr(self, "_" + command.replace(" ", "_"))
                return parser(user_input=normalized_input)
        raise ValueError("Unknown command!")

    def _hello(self, user_input: str):
        return "_hello", []

    def _add(self, user_input: str):
        args = user_input.lstrip("add ")
        username, phone = args.strip().split(" ")
        if username == "" or phone == "":
            raise ValueError("Bad input")
        else:
            return "add", [username, phone]

    def _change(self, user_input: str):
        args = user_input.replace("change ", "")
        username, old_phone, new_phone = args.strip().split(" ")
        if username == "" or old_phone == "" or new_phone == "":
            raise ValueError("Bad input")
        else:
            return "change", [username, old_phone, new_phone]

    def _phone(self, user_input: str):
        username = user_input.strip().lstrip("phone ")
        if username == "":
            raise ValueError("Bad input")
        else:
            return "phone", [username]

    def _show_all(self, user_input: str):
        if user_input == "show all ":
            return "show all", []
        else:
            raise ValueError("Bad input")

    def _exit(self, user_input: str):
        for item in ["good bye ", "close ", "exit "]:
            if item == user_input:
                return "exit", []
        raise ValueError("Bad input")

    def _good_bye(self, user_input: str):
        return self._exit(user_input)

    def _close(self, user_input: str):
        return self._exit(user_input)

    def _find(self, user_input: str):
        args = user_input.lstrip("find ")
        pattern = args.strip()
        if pattern != "":
            return "find", [pattern]
        raise ValueError("Bad input")

class CLI:
    def __init__(self):
        self._book = None
        self._parsers = InputParser()

    @command_handler
    def _hello_handler(self, *args):
        return "How can I help you?"

    @command_handler
    def add_handler(self, username: str, number: str):
        if self._book.find_name(username) is None:
            record = Record(name=Name(username), phone=Phone(number))
            self._book.add_record(record)
            return "Number was added!!!"
        raise ValueError("Number already in contact book!")

    @command_handler
    def change_handler(self, username: str, old_number: str, new_number: str):
        current_record: Record = self._book.find_name(username)
        if current_record is None:
            raise ValueError("Contact does not exists!")
        old_phone = current_record.find_phone(old_number)
        if old_phone is None:
            raise IndexError("Number does not exists!")
        new_phone = Phone(new_number)

        current_record.change_phone(old_phone, new_phone)
        return "Number was changed!!!"

    @command_handler
    def phone_handler(self, username: str):
        current_record: Record = self._book.find_name(username)
        if current_record is not None:
            return str(current_record)
        raise ValueError

    @command_handler
    def show_all_handler(self, *args):
        all_response = "Contact book\n"
        contacts = "\n".join(str(record) for record in list(self._book.data.values()))
        formatted_contacts = (
            "Contacts does not exists, yet!" if contacts == "" else contacts
        )
        return all_response + formatted_contacts

    @command_handler
    def exit_handler(self, *args):
        raise SystemExit("Good bye!!!")

    @command_handler
    def unknown_handler(self, *args):
        raise ValueError("Command is not valid!")

    @command_handler
    def find_handler(self, pattern):
        all_response = "Contact book\n"
        contacts = "\n".join(
            str(record) for record in list(self._book.find_by_pattern(pattern))
        )
        formatted_contacts = (
            "Contacts by query does not exists!" if contacts == "" else contacts
        )
        return all_response + formatted_contacts

    def setup_book(self, book):
        self._book = book

    def run(self):

        with AddressBook() as book:
            self.setup_book(book)

            while True:
                user_input = input("Command: ")
                result = self._parsers.parse_user_input(user_input=user_input)
                if len(result) != 2:
                    print(result)
                    continue
                command, arguments = result
                command_function = getattr(self, command.replace(" ", "_") + "_handler")
                try:
                    command_response = command_function(*arguments)
                    print(command_response)
                except SystemExit as e:
                    print(str(e))
                    break


if __name__ == "__main__":
    cli = CLI()
    cli.run()
