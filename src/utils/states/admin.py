from aiogram.fsm.state import StatesGroup, State


class PromoCodeStates(StatesGroup):
    username = State()
    discount = State()


class JobStates(StatesGroup):
    title = State()
    description = State()
    technology = State()
    images = State()
