from aiogram.fsm.state import StatesGroup, State


class TestStates(StatesGroup):
    text = State()
    is_test = State()


class OrderStates(StatesGroup):
    order_type = State()
    description = State()
    tech_task_filename = State()
