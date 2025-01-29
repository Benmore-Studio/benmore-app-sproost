
from profiles.models import ContractorProfile, UserProfile, AgentProfile
from django.db.models import Q


from profiles.services.contractor import ContractorService
from django.contrib.auth import get_user_model


from rest_framework.parsers import MultiPartParser


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.generics import  ListAPIView

from django.shortcuts import get_object_or_404

from quotes.models import QuoteRequest, Project,Review, UserPoints, Bid,ProjectPictures 
from .serializers import (ContractorProfileSerializer, 
                          ProfilePictureSerializer, 
                          HomeOwnerProfileSerializer, 
                          AgentProfileSerializer, 
                          ContractorSerializer,
                          
                        )
from profiles.services.contractor import ContractorService
from profiles.serializers import UserSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample







User = get_user_model()


def get_user_data(request):
    user = (
        User.objects
        .select_related('user_profile')  
        
        # Prefetch the reverse/Many relationships:
        .prefetch_related(
           'property_owner','quote_requests','user_profile__home_owner_invited_agents',
                'user_profile__home_owner_associated_contarctors'
            
            # Prefetch(
            #     'property_owner__quote_properties',  # chain: user -> property_owner -> quote_properties
            #     # Optional custom queryset, e.g. to filter only certain quotes:
            #     queryset=QuoteRequest.objects.all()
            # ),
            
         
        )
        .get(id=request.user.id)
    )
   
    serializer = UserSerializer(user)
    return serializer.data



def award_points(user, points):
    if hasattr(user, 'points'):
        user.points.add_points(points)
    else:
        UserPoints.objects.create(user=user, total_points=points)


# the vieew to route the home owner with slug
class HomeOwnerWithSlugNameView(APIView):
    """
    Retrieves home owner details using slug and returns their projects and quotes.

    ----------------------------
    INPUT PARAMETERS:
    - name: str (slug of the user)

    -----------------------------
    OUTPUT PARAMETERS:
    Returns home owner data and associated projects and quotes.
    """
    
    @extend_schema(
        responses={
            200: OpenApiResponse(description="Homeowner data and associated projects and quotes"),
            404: OpenApiResponse(description="Homeowner not found"),
        }
    )

    def get(self, request, name, *args, **kwargs):
        user = get_object_or_404(User, slug=name)
        context = home_owner_function(request, user)
        context['name'] = name
        return Response(context, status=status.HTTP_200_OK)


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


class UploadPicturesView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pictures = request.FILES.getlist('pictures')
        project_id = request.data.get('project_id')

        if not project_id:
            return Response({"error": "Project ID is required."}, status=400)

        if not pictures:
            return Response({"error": "No pictures were uploaded."}, status=400)

        # Save uploaded pictures
        for picture in pictures:
            ProjectPictures.objects.create(user=request.user, project_id=project_id, image=picture)

        # Count total pictures uploaded by the user for the project
        total_pictures = ProjectPictures.objects.filter(user=request.user, project_id=project_id).count()

        # Award points if total pictures reach or exceed 9
        if total_pictures >= 9:
            award_points(request.user, 3000)  # e.g., 3000 points for 9+ pictures

        return Response({"message": "Pictures uploaded successfully.", "total_pictures": total_pictures})


class WinBidView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        bid_id = request.data.get('bid_id')

        if not bid_id:
            return Response({"error": "Bid ID is required."}, status=400)

        # Retrieve the bid and check if it's a winning bid for the requesting user
        bid = Bid.objects.filter(id=bid_id, user=request.user).first()

        if not bid:
            return Response({"error": "Bid not found or does not belong to you."}, status=404)

        if not bid.is_winner:
            return Response({"error": "This bid is not marked as a winner."}, status=400)

        # Award points for winning the bid
        award_points(request.user, 5000)  # e.g., 5000 points for winning a bid
        return Response({"message": "Points awarded for winning the bid."})


class RateContractorView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        contractor_id = request.data.get('contractor_id')
        rating = request.data.get('rating')
        comments = request.data.get('comments', '')

        if not contractor_id or not rating:
            return Response({"error": "Contractor ID and rating are required."}, status=400)

        # Create the review
        Review.objects.create(
            user=request.user,
            contractor_id=contractor_id,
            rating=rating,
            comments=comments
        )

        # Award points for reviewing a contractor
        award_points(request.user, 1000)  # e.g., 1000 points for reviewing a contractor

        return Response({"message": "Review submitted successfully."})


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


    

