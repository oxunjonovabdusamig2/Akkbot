from aiogram.fsm.state import State, StatesGroup


class AddAccount(StatesGroup):
    photo = State()
    video = State()
    price = State()
    privyazka = State()
    description = State()
    confirm = State()


class EditAccount(StatesGroup):
    waiting_id = State()
    choosing_field = State()
    waiting_value = State()


class SoldAccount(StatesGroup):
    waiting_id = State()


class RelistAccount(StatesGroup):
    waiting_id = State()


class DeleteAccount(StatesGroup):
    waiting_id = State()
    confirm = State()


class PinAccount(StatesGroup):
    waiting_id = State()


class SearchAccount(StatesGroup):
    waiting_id = State()


class AddAdmin(StatesGroup):
    waiting_id = State()


class RemoveAdmin(StatesGroup):
    waiting_id = State()
