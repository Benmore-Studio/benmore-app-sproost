from accounts.services.user import UserService
from main.models import Media, MediaTypes
from quotes.models import QuoteRequest
from services.model_actions import ModelAction
from services.utils import CustomRequestUtil


class QuoteService(CustomRequestUtil):
    def __init__(self, request):
        super().__init__(request)

    def create(self, payload):
        try:
            media = payload.pop("media")
            home_owner_id = payload.pop("home_owner_id")

            # payload['user'] = self.request.user

            if home_owner_id:
                user_service = UserService(self.request)
                user, error = user_service.fetch_single_by_pk(id=home_owner_id)

                if error:
                    return None, error

                payload['user'] = user

            image_types = {'jpg', 'png', 'svg', 'jpeg'}
            file_types = {'pdf'}
            video_types = {'mp4', 'mkv', 'webm'}

            model_action_service = ModelAction(self.request)
            quote, error = model_action_service.create_model_instance(model=QuoteRequest, payload=payload)

            if error:
                return None, error



            if media:
                for file in media:
                    media_file, media_image,media_video = None, None, None

                    extension = file.name.split('.')[-1].lower()

                    if extension in file_types:
                        media_file = file
                    elif extension in image_types:
                        media_image = file
                    elif extension in video_types:
                        media_video = file

                    quote.media_paths.create(
                        content_object=quote,
                        image=media_image,
                        file=media_file,
                        video=media_video
                    )

            return "Quote Request saved successfully", None

        except Exception as e:

            return None, self.make_error("An error occurred!", error=e)