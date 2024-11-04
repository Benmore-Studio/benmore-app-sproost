from accounts.models import User
from services.utils import CustomRequestUtil


class UserService(CustomRequestUtil):
    def __init__(self, request):
        super().__init__(request)

    def fetch_single_by_pk(self, id):
        try:
            user = User.objects.get(pk=id)

            return user, None

        except User.DoesNotExist:
            return None, self.make_error("User does not exist!")
        
        except Exception as e:
            return None, self.make_error("An error occured!", error=e)