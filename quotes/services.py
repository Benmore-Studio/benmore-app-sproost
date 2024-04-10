from main.models import Media, MediaTypes
from quotes.models import QuoteRequests
from services.model_actions import ModelAction
from services.utils import CustomRequestUtil


class QuoteService(CustomRequestUtil):
    def __init__(self, request):
        super().__init__(request)

    def create(self, payload):
        media = payload.pop("media")

        payload['user'] = self.request.user

        image_types = {'jpg', 'png', 'svg', 'jpeg'}
        file_types = {'pdf'}

        try:
            model_action_service = ModelAction(self.request)
            quote, error = model_action_service.create_model_instance(model=QuoteRequests, payload=payload)

            if error:
                return None, error
            
            payload.pop("user")

            for file in media:
                extension = file.name[1].lower()
                media_type = MediaTypes.image

                if extension in file_types:
                    media_type = MediaTypes.file

                quote_media = Media(
                    content_object=quote,
                    media_type=media_type,
                    file_path=file,
                )

                quote_media.save()

            return "Quote Request saved successfully", None


        except Exception as e:
            return None, self.make_error("An error occurred!", error=e)