from services.utils import CustomRequestUtil


class ContractorService(CustomRequestUtil):
    def __init__(self, request):
        super().__init__(request)

    def add_media(self, data):
        media = data.get("media")
        contractor = self.request.user.contractor_profile
        
        image_types = {'jpg', 'png', 'svg', 'jpeg'}
        file_types = {'mp4','mkv','m4a'}

        try:
            for file in media:
                media_file, media_image = None, None

                extension = file.name.split('.')[-1].lower()

                if extension in file_types:
                    media_file = file
                elif extension in image_types:
                    media_image = file

                contractor.media_paths.create(
                    content_object=contractor,
                    image=media_image,
                    file=media_file
                )

            return "Media saved successfully", None

        except Exception as e:
            return None, self.make_error("An error occurred!", error=e)
