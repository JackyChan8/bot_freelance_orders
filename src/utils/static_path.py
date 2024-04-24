import os

current_path = os.getcwd()


def get_parent_dir() -> str:
    return os.path.dirname(current_path)


COMPANY_LOGO = get_parent_dir() + '/static/codewave_studio.jpg'
ORDERS_FILES = get_parent_dir() + '/static/orders/'
JOBS_FILES = get_parent_dir() + '/static/jobs_photos/'
