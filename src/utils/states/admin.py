from aiogram.fsm.state import StatesGroup, State


class PromoCodeStates(StatesGroup):
    username = State()
    discount = State()


class JobStates(StatesGroup):
    title = State()
    description = State()
    technology = State()
    images = State()


class ProjectEditStates(StatesGroup):
    field = State()
    project_id = State()
    text = State()
    images = State()
