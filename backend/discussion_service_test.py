#Author: Vodohleb04
import broker


from backend.service_layer.authentication_service.authorization_token import AuthorizationToken
from broker.discussion_tasks import DiscussionTasks



result = broker.DiscussionTasks.get_discussion_categories_task.delay()
print(result.get())


result = broker.DiscussionTasks.get_all_discussions_task.delay()
print(result.get())


result = broker.DiscussionTasks.get_discussion_by_title_task.delay("Trash")
print(result.get())


result = broker.DiscussionTasks.get_discussions_by_category_task.delay("Hernya")
print(result.get())




this_token = AuthorizationToken("user", "<PASSWORD>", False)
other_token = AuthorizationToken("other_user", "pppp", False)
admin_token = AuthorizationToken("admin", "plan", True)


from backend.data_access_layer.discussion_dal.save_discussion_dto import SaveDiscussionDTO

discussion_item = SaveDiscussionDTO(
    title="Which car is the best?",
    description="Двойки, восьмёрки, тройки и девятки - самые лучшие тачки...",
    category="Cars",
    sender_login="user"
)

#result = broker.DiscussionTasks.save_discussion_task.delay(discussion_item, this_token)
#result.get()

result = broker.DiscussionTasks.get_discussion_by_title_task.delay("Which car is the best?")
print(result.get())


#result = broker.DiscussionTasks.delete_comment_by_id_task.delay(2, admin_token)
#result.get()
#result = broker.DiscussionTasks.delete_discussion_by_title_task.delay("Fready Fazber discussion", admin_token)
#result.get()



from backend.data_access_layer.comment_dal.save_comment_dto import SaveCommentDTO
comment = SaveCommentDTO(
    description="Лучше бы вы взяли старинную фирмУ...",
    sender_login="other_user",
    discussion_title="Which car is the best?"
)


#result = broker.DiscussionTasks.save_comment_task.delay(comment, other_token)
#result.get()

result = broker.DiscussionTasks.get_comment_by_id_task.delay(7)
print(result.get().description)







