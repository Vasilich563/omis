#Author: Vodohleb04
from celery import Celery


CELERY_SETTINGS = {
    'CELERY_TASK_SERIALIZER': 'pickle',
    'CELERY_RESULT_SERIALIZER': 'pickle',
    'CELERY_ACCEPT_CONTENT': ['pickle', 'json'],
}


broker_app = Celery('broker', broker='redis://localhost:6379', backend='redis://localhost:6379')
broker_app.conf.update(CELERY_SETTINGS)


if __name__ == '__main__':
    broker_app.start()
