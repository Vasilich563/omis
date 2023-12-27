#Author: Vodohleb04
import broker



from backend.service_layer.authentication_service.authorization_token import AuthorizationToken




result = broker.KnowledgeTasks.get_knowledge_categories_task.delay()
print(result.get())


result = broker.KnowledgeTasks.get_knowledge_by_title_task.delay("Fready Fazber knowledge")
print(result.get())


result = broker.KnowledgeTasks.get_knowledge_by_category_task.delay("Fready Fazber")
print(result.get())


result = broker.KnowledgeTasks.get_knowledge_by_category_list_task.delay(["Fready Fazber"])
print(result.get())


result = broker.KnowledgeTasks.get_published_knowledge_task.delay()
print(result.get())


this_token = AuthorizationToken("user", "<PASSWORD>", False)
other_token = AuthorizationToken("other_user", "pppp", False)
admin_token = AuthorizationToken("admin", "plan", True)


result = broker.KnowledgeTasks.get_in_processing_knowledge_task.delay(admin_token)
print(result.get())


from backend.data_access_layer.knowledge_dal.save_knowledge_dto import SaveKnowledgeDTO

knowledge_item = SaveKnowledgeDTO(
    title="OPG of Shmalinovka",
    description="Today we will speak about opg of shmalinovka",
    link="www.google.com",
    category="True crime",
    sender_login="user"
)
#result = broker.KnowledgeTasks.save_knowledge_task.delay(knowledge_item, this_token)
#result.get()
result = broker.KnowledgeTasks.get_knowledge_by_title_task.delay("OPG of Shmalinovka")
print(result.get())



result = broker.KnowledgeTasks.accept_knowledge_publishing_task.delay("OPG of Shmalinovka", admin_token)
result.get()


result = broker.KnowledgeTasks.get_published_knowledge_task.delay()
print(result.get())


result = broker.KnowledgeTasks.delete_knowledge_by_title_task.delay("OPG of Shmalinovka", this_token)
result.get()
