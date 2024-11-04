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

            print("Media:", media)

            image_types = {'jpg', 'png', 'svg', 'jpeg'}
            file_types = {'pdf'}
            video_types = {'mp4', 'mkv', 'webm'}

            model_action_service = ModelAction(self.request)
            quote, error = model_action_service.create_model_instance(model=QuoteRequest, payload=payload)
    
            if error:
                # print("Error during QuoteRequest creation:", error)
                return None, error

            # print("QuoteRequest created:", quote)


            if media:
                print(" ")
                print("yes")
                for file in media:
                    media_file, media_image,media_video = None, None, None

                    extension = file.name.split('.')[-1].lower()
                    if extension in file_types:
                        media_file = file
                    elif extension in image_types:
                        media_image = file
                        print(media_image)
                        print("media")
                    elif extension in video_types:
                        media_video = file

                    quote.media_paths.create(
                        content_object=quote,
                        image=media_image,
                        file=media_file,
                        video=media_video
                    )

            return quote, None

        except Exception as e:
            return None, self.make_error("An error occurred!", error=e)
        
