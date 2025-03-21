from django.shortcuts import render

# Create your views here.

from django.http import JsonResponse
import cloudinary.uploader

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import cloudinary.uploader

class DeleteMediaView(APIView):
    """Handles media deletion from Cloudinary"""

    def delete(self, request, public_id):
        """Delete media from Cloudinary"""
        result = cloudinary.uploader.destroy(public_id)
        return Response({"status": "deleted", "result": result}, status=status.HTTP_200_OK)



# ok, first you need to convert to drf class based views-from django.http import JsonResponse
# import cloudinary.uploader

# def delete_media(request, public_id):
#     """Delete media from Cloudinary"""
#     result = cloudinary.uploader.destroy(public_id)
#     return JsonResponse({"status": "deleted", "result": result}) , secondly you ddnt give me the html struture with is description of where to plu this functions, lastly you added message to my media model? whats that field for and why?-class Media(models.Model):
#     message = models.ForeignKey(Message, related_name="media", on_delete=models.CASCADE)
#     url = models.URLField()
#     public_id = models.CharField(max_length=255)  # Cloudinary ID for deletion
#     media_type = models.CharField(max_length=10, choices=[("image", "Image"), ("video", 
