from main.models import Media, MediaTypes
from quotes.models import QuoteRequest
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
            quote, error = model_action_service.create_model_instance(model=QuoteRequest, payload=payload)

            if error:
                return None, error

            for file in media:
                media_file, media_image = None, None

                extension = file.name.split('.')[-1].lower()

                if extension in file_types:
                    media_file = file
                elif extension in image_types:
                    media_image = file

                quote.media_paths.create(
                    content_object=quote,
                    image=media_image,
                    file=media_file
                )

            return "Quote Request saved successfully", None


        except Exception as e:
            return None, self.make_error("An error occurred!", error=e)