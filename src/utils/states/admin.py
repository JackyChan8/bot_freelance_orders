from aiogram.fsm.state import StatesGroup, State


class PromoCodeStates(StatesGroup):
    username = State()
    discount = State()
