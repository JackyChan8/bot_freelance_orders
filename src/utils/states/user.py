from aiogram.fsm.state import StatesGroup, State


class OrderStates(StatesGroup):
    order_type = State()
    description = State()
    tech_task_filename = State()


class ReviewStates(StatesGroup):
    text = State()
    rating = State()
