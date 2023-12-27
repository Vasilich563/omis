#Author: Vodohleb04
from .celery_broker import broker_app
from .authentication_tasks import AuthenticationTasks
from .knowledge_tasks import KnowledgeTasks
from .discussion_tasks import DiscussionTasks
