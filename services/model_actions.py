from  .utils import CustomRequestUtil
from profiles.models import UserProfile
from accounts.models import User
from quotes.models import Property


class ModelAction(CustomRequestUtil):
    def __init__(self, request, user_profile):
        self.request = request

    def create_model_instance(self, model=None, payload={}, user_profile=""):
        try:
            if model is None:
                error = "Invalid model instance"
                return None, self.make_error(error=error)

            print("hello", model)
            # if model == User:
            #     payload["user"] = user_profile
            main_object = model.objects.create(**payload)
            main_object.save()

            return main_object, None
        
        except Exception as e:
            return None, self.make_error("An error occurred!", error=e)


    def update_model_instance(self, model_instance=None, **kwargs):
        try:
            if model_instance is None:
                error = "Invalid model instance"
                return None, self.make_error(error=error)
            
            update_fields = []
            for field, value in kwargs.items():
                setattr(model_instance, field, value)
                update_fields.append(field)

            model_instance.save(update_fields=update_fields)

            return model_instance, None

        except Exception as e:
            return None, self.make_error("An error occurred!", error=e)
        