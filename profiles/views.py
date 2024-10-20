
from profiles.models import ContractorProfile, UserProfile, AgentProfile
from django.db.models import Q


from profiles.services.contractor import ContractorService
from django.contrib.auth import get_user_model



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.generics import  ListAPIView

from django.shortcuts import get_object_or_404

from profiles.models import ContractorProfile
from quotes.models import QuoteRequest, Project
from .serializers import (ContractorProfileSerializer, 
                          ProfilePictureSerializer, 
                          HomeOwnerProfileSerializer, 
                          AgentProfileSerializer, 
                          ContractorSerializer,
                        )
from profiles.services.contractor import ContractorService






User = get_user_model()

def home_owner_function(request, value):
    quotes = QuoteRequest.objects.filter(user=value)
    projects = Project.objects.filter(quote_request__user=value)
    projs = Project.objects.filter(admin=value)
    context ={
        "quotes": quotes,
        "projects": projects,
        'projs':projs,
        "quote_count": quotes.count(),
        "projects_count": projects.count(),
        "home_owner_slug": request.user.slug
    }
    return context



# # the vieew to route the home owner with slug
# class HomeOwnerWithSlugNameView(APIView):
#     """
#     Retrieves home owner details using slug and returns their projects and quotes.

#     ----------------------------
#     INPUT PARAMETERS:
#     - name: str (slug of the user)

#     -----------------------------
#     OUTPUT PARAMETERS:
#     Returns home owner data and associated projects and quotes.
#     """
    
#     @extend_schema(
#         responses={
#             200: OpenApiResponse(description="Homeowner data and associated projects and quotes"),
#             404: OpenApiResponse(description="Homeowner not found"),
#         }
#     )

#     def get(self, request, name, *args, **kwargs):
#         user = get_object_or_404(User, slug=name)
#         context = home_owner_function(request, user)
#         context['name'] = name
#         return Response(context, status=status.HTTP_200_OK)


# class ContractorProfileAPIView(APIView):
#     """
#     API View to handle contractor profile view and media uploads. to be used in main app
#     """
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         """
#         Retrieve the contractor's profile details.
#         """
#         if request.user.user_type != 'CO':
#             return Response({'error': 'Unauthorized access'}, status=status.HTTP_403_FORBIDDEN)

#         try:
#             profile = User.objects.get(id=request.user.id)
#             serializer = ContractorSerializer(profile) 
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except ContractorProfile.DoesNotExist:
#             return Response({'error': 'Contractor profile not found'}, status=status.HTTP_404_NOT_FOUND)



class EditUsersProfileAPIView(APIView):
    """
    API View to handle the update of user profiles (Home Owner, Contractors and Agent) using PATCH for partial updates.
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user

        if user.user_type == 'HO':
            user_profile = get_object_or_404(UserProfile, user=user)
            serializer_class = HomeOwnerProfileSerializer
        elif user.user_type == 'AG':
            user_profile = get_object_or_404(AgentProfile ,user=user)
            serializer_class = AgentProfileSerializer
        elif user.user_type == 'CO':
            user_profile = get_object_or_404(ContractorProfile ,user=user)
            serializer_class = ContractorProfileSerializer
        else:
            return Response({'error': 'User type not found for profile update.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = serializer_class(user_profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            if 'phone_number' in serializer.validated_data:
                user.phone_number = serializer.validated_data['phone_number']
            if 'email' in serializer.validated_data:
                user.email = serializer.validated_data['email']
            if 'image' in request.FILES:
                user.image = request.FILES['image']
            user.save()

            return Response({'message': 'Profile updated successfully!'}, status=status.HTTP_200_OK)

        # Debugging for error messages
        print("Serializer errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContractorSearchAPIView(ListAPIView):
    """
    API View to search contractor profiles based on query.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ContractorProfileSerializer

    def get_queryset(self):
        query = self.request.GET.get('query', '')
        queryset = ContractorProfile.objects.all()
        if query:
            queryset = queryset.filter(
                Q(company_name__icontains=query) |
                Q(specialization__icontains=query) |
                Q(user__phone_number__icontains=query) |
                Q(user__email__icontains=query)
            )
        return queryset


class ChangeProfilePictureAPIView(APIView):
    """
    API View to change profile pictures based on user type.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        form = ProfilePictureSerializer(data=request.data)
        if form.is_valid():
            image_instance = image_instance = form.validated_data.get('image', None)

            if image_instance is None:
                return Response({'error': 'Please select an image'}, status=status.HTTP_400_BAD_REQUEST)



            # Get or create the profile based on the user type
            if request.user.user_type == 'CO':
                contractor_profile = ContractorProfile.objects.get(user=request.user)
                contractor_profile.image = image_instance
                contractor_profile.save()
            elif request.user.user_type == 'HO':
                home_owner_profile = UserProfile.objects.get(user=request.user)
                home_owner_profile.image = image_instance
                home_owner_profile.save()
            elif request.user.user_type == 'AG':
                agent_profile = AgentProfile.objects.get(user=request.user)
                agent_profile.image = image_instance
                agent_profile.save()
            else:
                return Response({'error': 'Invalid user type'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'message': 'Profile picture changed successfully!'}, status=status.HTTP_200_OK)
        else:
            # Handle errors
            self.stdout.write('ff')
            print("ff")
            image_errors = form.errors.get('image', [])
            for error in image_errors:
                if error == 'This field is required':
                    return Response({'error': 'Please select an image'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'error': f'An Error Occurred, {error}'}, status=status.HTTP_400_BAD_REQUEST)


class UploadApiView(APIView):
    """
    API View to handle contractor media uploads.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Handle media uploads for contractor profiles.
        """
        if request.user.user_type != 'CO':
            return Response({'error': 'Unauthorized access'}, status=status.HTTP_403_FORBIDDEN)

        if request.FILES:
            media = request.FILES.getlist("upload-media")
            data = {"media": media}
            contractor_service = ContractorService(request=request)
            add_media, error = contractor_service.add_media(data)

            if error:
                return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'message': add_media}, status=status.HTTP_200_OK)
        
        return Response({'error': 'No file found!'}, status=status.HTTP_400_BAD_REQUEST)


# class EditProfileAPIView(APIView):
#     """
#     API View to edit user profiles based on user type (CO, AG, HO), this returns initial data to prefill the form with.
#     """
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         if user.user_type == 'CO':
#             profile = ContractorProfile.objects.get(user=user)
#             serializer = ContractorProfileSerializer(profile)
#         elif user.user_type == 'AG':
#             profile = AgentProfile.objects.get(user=user)
#             serializer = AgentProfileSerializer(profile)
#         elif user.user_type == 'HO':
#             profile = UserProfile.objects.get(user=user)
#             serializer = HomeOwnerProfileSerializer(profile)
#         else:
#             return Response({'error': 'Invalid user type'}, status=status.HTTP_400_BAD_REQUEST)
        
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def post(self, request):
#         user = request.user
#         if user.user_type == 'CO':
#             profile = ContractorProfile.objects.get(user=user)
#             serializer = ContractorProfileSerializer(profile, data=request.data)
#         elif user.user_type == 'AG':
#             profile = AgentProfile.objects.get(user=user)
#             serializer = AgentProfileSerializer(profile, data=request.data)
#         elif user.user_type == 'HO':
#             profile = UserProfile.objects.get(user=user)
#             serializer = HomeOwnerProfileSerializer(profile, data=request.data)
#         else:
#             return Response({'error': 'Invalid user type'}, status=status.HTTP_400_BAD_REQUEST)

#         if serializer.is_valid():
#             serializer.save()
#             return Response({'message': 'Profile updated successfully!'}, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    

