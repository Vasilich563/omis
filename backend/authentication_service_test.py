#Author: Vodohleb04
import broker

result = broker.AuthenticationTasks.get_user_by_login_task.delay("user")
print(result.get())

from backend.data_access_layer.user_dal.login_user_dto import LoginUserDTO
from backend.service_layer.authentication_service.authentication_error import AuthenticationError
try:
    result = broker.AuthenticationTasks.login_task.delay(LoginUserDTO("user", "<PASSWORD>"))
    print(result.get().get_login())
except AuthenticationError:
    print('wrong password')

import datetime
from backend.data_access_layer.user_dal.save_user_dto import SaveUserDTO
try:
    result = broker.AuthenticationTasks.register_task.delay(
        SaveUserDTO(
            True,
            "rogonosec",
            "kukold",
            "zena nastavila roga",
            "roga@rogonosec.mail.ru",
            datetime.date.today(),
            "rogonosec"
        )
    )
    print(result.get().get_login())
except ValueError:
    print("User already exists")

