
from drf_spectacular.utils import extend_schema,extend_schema_view, OpenApiParameter, OpenApiTypes

from rest_framework.parsers import MultiPartParser
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, generics
from rest_framework.generics import  ListAPIView
from django.conf import settings
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from profiles.models import ContractorProfile, UserProfile, AgentProfile, Invitation
from profiles.services.contractor import ContractorService
from property.models import Property
from quotes.models import QuoteRequest, Project,Review, UserPoints, Bid,ProjectPictures 
from .serializers import (SimpleContractorProfileSerializer, 
                          ProfilePictureSerializer, UserSerializer,
                          SimpleHomeOwnerProfileSerializer, 
                          SimpleAgentProfileSerializer, AgentSerializer,
                          ContractorSerializer,SimplePropertySerializer,HomeOwnerSerializer,
                          PolymorphicUserSerializer, AgentUserSerializer, InvitationSerializer

                          
                        )
from .utils import send_invitation_email


from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from chat.models import ChatRoom, Message


User = get_user_model()


class GetUserListingsOrProperties(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SimplePropertySerializer

    def get_queryset(self):
        return Property.objects.filter(property_owner=self.request.user).prefetch_related('media_paths')

    

class GetUserClientsOrAgents(ListAPIView):
    """
    List of invited agents (if user is HO) or invited homeowners (if user is AG). 
    The query types are different users-(AG,CO and HO). 
    if you are trying to see the agents associated to house owners, query type = AG, 
    if you are trying to see the house owners associated to agents, query type = HO, 
    if you are trying to see the contractors associated to house owners, query type = CO and vice versa
      
    """

    permission_classes = [IsAuthenticated] 

    @extend_schema(
    summary="Get User Clients or Agents",
    description="""
        **List of invited agents (if user is HO) or invited homeowners (if user is AG).**

        - **Home Owners (HO):**
        - `query_type=AG` → Returns invited agents
        - `query_type=CO` → Returns associated contractors

        - **Agents (AG):**
        - `query_type=HO` → Returns invited homeowners
        - `query_type=CO` → Returns associated contractors

        Provide the appropriate `query_type` in the **URL** (or query param). 
        If an invalid value is supplied for the user type, a validation error is raised.
        """,
    parameters=[
        OpenApiParameter(
            name="query_type",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,  # or QUERY if you're using ?query_type=...
            required=True,
            description="Allowed values: 'AG', 'HO', or 'CO'."
        )
    ],
    responses={
        200: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT,
    },
)
    def get_queryset(self):
        user = self.request.user
        query_type = self.kwargs.get('query_type')
        if user.user_type == 'HO':
            if query_type == "AG":
                return (
                    user.user_profile
                    .home_owner_invited_agents
                    .select_related("agent_profile")
                    .all()
                )
            elif query_type == "CO":
                return (
                    user.user_profile
                    .home_owner_associated_contarctors
                    .select_related("contractor_profile")
                    .all()
                )
            else:
                raise ValidationError("Invalid query_type for the requesting user type.")
        elif user.user_type == 'AG':
            if query_type == "HO":
                return (
                    user.agent_profile
                    .agent_invited_home_owners
                    .select_related("user_profile")
                    .all()
                )
            elif query_type == "CO":
                return (
                    user.agent_profile
                    .agent_associated_contarctors
                    .select_related("user_profile")
                    .all()
                )
            else:
                raise ValidationError("Invalid query_type for the requesting user type.")
        else:
            return User.objects.none()
    def get_serializer_class(self):
        # Always return the polymorphic serializer
        return PolymorphicUserSerializer
        

class EditUsersProfileAPIView(APIView):
    """
    API View to handle the update of user profiles (Home Owner, Contractors, and Agent) using PATCH for partial updates.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Edit User Profile",
        description="""
        Allows authenticated users (`Home Owner`, `Agent`, `Contractor`) to update their profile information.

        **User Types Supported:**
        - `HO` (Home Owner)
        - `AG` (Agent)
        - `CO` (Contractor)

        **Fields That Can Be Updated:**
        - `phone_number`
        - `email`
        - `first_name`
        - `last_name`
        - `image` (Profile Picture)

        **User Type-Based Profile Updates:**
        - Home Owners → `UserProfile`
        - Agents → `AgentProfile`
        - Contractors → `ContractorProfile`
        """,
        request={
        "application/json": {
            "type": "object",
            "properties": {
                "phone_number": {"type": "string", "description": "User's phone number"},
                "email": {"type": "string", "description": "User's email address"},
                "first_name": {"type": "string", "description": "User's first name"},
                "last_name": {"type": "string", "description": "User's last name"},
                "image": {"type": "string", "format": "binary", "description": "User's profile picture"},
            }
        }
        },
    
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
        },
    )


    def patch(self, request):
        user = request.user

        # Determine the user profile and serializer based on user type
        if user.user_type == 'HO':
            user_profile = get_object_or_404(UserProfile, user=user)
            serializer_class = SimpleHomeOwnerProfileSerializer
        elif user.user_type == 'AG':
            user_profile = get_object_or_404(AgentProfile, user=user)
            serializer_class = SimpleAgentProfileSerializer
        elif user.user_type == 'CO':
            user_profile = get_object_or_404(ContractorProfile, user=user)
            serializer_class = SimpleContractorProfileSerializer
        else:
            return Response({'error': 'User type not found for profile update.'}, status=status.HTTP_400_BAD_REQUEST)

        # Update user model fields before saving
        user_data_updated = False
        if 'phone_number' in request.data:
            user.phone_number = request.data['phone_number']
            user_data_updated = True
        if 'email' in request.data:
            user.email = request.data['email']
            user_data_updated = True
        if 'first_name' in request.data:
            user.first_name = request.data['first_name']
            user_data_updated = True
        if 'last_name' in request.data:
            user.last_name = request.data['last_name']
            user_data_updated = True
        if 'image' in request.FILES:
            user.image = request.FILES['image']
            user_data_updated = True

        if user_data_updated:
            user.save()  

        # Update the profile model
        serializer = serializer_class(user_profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            # Return updated user and profile data
            return Response({
                'message': 'Profile updated successfully!',
                'user': {
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone_number': str(user.phone_number), 
                },
                'profile': serializer.data 
            }, status=status.HTTP_200_OK)

        # Debugging for error messages
        print("Serializer errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContractorSearchAPIView(ListAPIView):
    """
    API View to search contractor profiles based on query.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SimpleContractorProfileSerializer

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

    @extend_schema(
        summary="Change Profile Picture",
        description="""
        Allows authenticated **contractors** (`user_type='CO'`) to upload a new profile picture.

        **Required Fields:**
        - `image` (Single File Upload): The new profile picture.

        **Restrictions:**
        - Only **contractors** (`user_type='CO'`) can update their profile pictures.
        """,
        parameters=[
            OpenApiParameter(
                name="image",
                type=OpenApiTypes.STR,
                required=True,
                description="The new profile picture (image file)."
            ),
        ],

        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
        },
    )

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
            image_errors = form.errors.get('image', [])
            for error in image_errors:
                if error == 'This field is required':
                    return Response({'error': 'Please select an image'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'error': f'An Error Occurred, {error}'}, status=status.HTTP_400_BAD_REQUEST)

# not needed - web-based
class ContractorUploadApiView(APIView):
    """
    API View to handle contractor media/project uploads.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Upload Contractor Media",
        description="""
        Allows authenticated contractors to upload project media files.

        **Required Fields:**
        - `media` (File Upload - Multiple Files Allowed): Images, videos, or document files.
        
        **Restrictions:**
        - Only users with `user_type='CO'` (Contractors) can upload.
        """,
        parameters=[
            OpenApiParameter(
                name="media",
                type=OpenApiTypes.STR,
                required=True,
                description="Multiple media files (images, videos, documents)."
            ),
        ],
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
        },
    )

    def post(self, request):
        """
        Handle media uploads for contractor profiles.
        """
        if request.user.user_type != 'CO':
            return Response({'error': 'Unauthorized access'}, status=status.HTTP_403_FORBIDDEN)

        if request.FILES:
            media = request.FILES.getlist("media")
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


class AllAgents(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AgentUserSerializer
    queryset = AgentProfile.objects.all()


class ContractorListAPIView(ListAPIView):
    """
    API View view all contractor profiles.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ContractorSerializer

    def get_queryset(self):
        return User.objects.select_related("contractor_profile").filter(user_type="CO", contractor_profile__isnull=False)
   
    


class UserSearchAPIView(APIView):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        if query:
            users = User.objects.filter(
                Q(username__icontains=query) | Q(email__icontains=query)
            )
            results = [
                {'id': user.id, 'username': user.username, 'email': user.email}
                for user in users
            ]
            return Response({'users': results})
        return Response({'users': []})


class CreateRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        room_name = request.data.get('roomName')
        member_ids = request.data.get('members', [])

        if not room_name:
            return Response({'error': 'Room name is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Optional: ensure uniqueness of room name
        if ChatRoom.objects.filter(name=room_name).exists():
            return Response({'error': 'A room with this name already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the room with the requesting user as creator
        chat_room = ChatRoom.objects.create(name=room_name, creator=request.user)
        
        # Add the creator to the room by default)
        chat_room.members.add(request.user)

        # Add each selected user
        for user_id in member_ids:
            try:
                user = User.objects.get(id=user_id)
                chat_room.members.add(user)
            except User.DoesNotExist:
                # Optionally handle this case if user doesn't exist
                pass
        
        print("ogo")
        # **Send WebSocket Notification to Connected Users**
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "global_notifications",  # Broadcast to all connected users
            {
                "type": "notify_new_room",
                "room": {
                    "id": chat_room.id,
                    "name": chat_room.name
                }
            }
        )
        print(chat_room.id, "✅ WebSocket event successfully sent!", chat_room.name)
        
        return Response({
            'success': True,
            'roomId': chat_room.id,
            'roomName': chat_room.name
        }, status=status.HTTP_201_CREATED)



class AddMembersAPIView(APIView):
    """ Allow only the room creator to add members to an existing chat room """
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        # Get the chat room
        chat_room = get_object_or_404(ChatRoom, id=room_id)

        # Ensure that only the room creator (admin) can add new members
        if chat_room.creator != request.user:
            return Response({'error': 'Only the room creator can add members.'}, status=status.HTTP_403_FORBIDDEN)

        # Get user IDs from request
        member_ids = request.data.get('members', [])

        if not member_ids:
            return Response({'error': 'No members provided to add.'}, status=status.HTTP_400_BAD_REQUEST)

        added_users = []
        for user_id in member_ids:
            try:
                user = User.objects.get(id=user_id)
                if user not in chat_room.members.all():  # Prevent duplicates
                    chat_room.members.add(user)
                    added_users.append(user.username)
            except User.DoesNotExist:
                continue  # Ignore invalid user IDs

        return Response({
            'success': True,
            'message': 'Users added successfully.',
            'added_users': added_users
        }, status=status.HTTP_200_OK)

class LeaveRoomAPIView(APIView):
    """ Allow a user to leave a chat room """
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        # Get the chat room
        chat_room = get_object_or_404(ChatRoom, id=room_id)

        # Ensure the user is in the chat room
        if request.user not in chat_room.members.all():
            return Response({'error': 'You are not a member of this chat room.'}, status=status.HTTP_400_BAD_REQUEST)

        # Remove the user from the room
        chat_room.members.remove(request.user)

        return Response({
            'success': True,
            'message': 'You have left the chat room.'
        }, status=status.HTTP_200_OK)


class SearchMessagesView(APIView):
    """
    API endpoint to search messages in chat rooms.
    Users can search globally or within a specific chat room.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '').strip()
        room_id = request.GET.get('room_id')  # Optional: filter messages by room

        if not query:
            return Response({"error": "Query is required"}, status=400)

        messages = Message.objects.filter(Q(content__icontains=query))

        if room_id:
            messages = messages.filter(room_id=room_id)

        results = [
            {
                "id": msg.id,
                "room_id": msg.room.id,
                "room_name": msg.room.name,
                "content": msg.content,
                "sender": msg.sender.username,
                "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            for msg in messages
        ]

        return Response({"results": results})



def award_points(user, points):
    if hasattr(user, 'points'):
        user.points.add_points(points)
    else:
        UserPoints.objects.create(user=user, total_points=points)



class InviteAgentView(generics.GenericAPIView):
    serializer_class = InvitationSerializer

    def post(self, request, *args, **kwargs):
        
        if request.user.user_type != 'AG':
            return Response({'errror': "you don't have permission to invite agents"}, status=status.HTTP_400_BAD_REQUEST)
        inviter = request.user
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the invitation instance; referral_code is auto-generated in save()
        invitation = Invitation.objects.filter(inviter=inviter, email=email).first()
        
        if invitation:
            send_invitation_email(email, invitation.referral_code)
              
        else:

            invitation = Invitation.objects.create(inviter=inviter, email=email)
            send_invitation_email(email, invitation.referral_code)



        serializer = self.get_serializer(invitation)         
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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

# the vieew to route the home owner with slug
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

