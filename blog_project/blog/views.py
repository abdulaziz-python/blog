from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from .models import Post, Category, Tag, PostImage, Reaction
from .serializers import (
    PostSerializer, PostListSerializer, PostDetailSerializer, PostCreateSerializer,
    CategorySerializer, TagSerializer, PostImageSerializer, ReactionSerializer
)
from .pagination import StandardResultsSetPagination

class IsAdminUserOrReadOnly(IsAuthenticated):
    """
    Custom permission to only allow admin users to edit.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Write permissions are only allowed to admin users
        return request.user and request.user.is_staff

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = StandardResultsSetPagination
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categories__slug', 'tags__slug', 'published']
    search_fields = ['title', 'content', 'excerpt']
    ordering_fields = ['created_at', 'updated_at', 'title']
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        elif self.action == 'retrieve':
            return PostDetailSerializer
        elif self.action == 'create':
            return PostCreateSerializer
        return PostSerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'upload_images']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        This view should return a list of all published posts
        for non-admin users, but all posts for admin users.
        """
        if self.request.user and self.request.user.is_staff:
            return Post.objects.all()
        return Post.objects.filter(published=True)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def upload_images(self, request, slug=None):
        """Upload multiple images to a post"""
        post = self.get_object()
        
        # Handle multiple image uploads
        images = request.FILES.getlist('images')
        if not images:
            return Response(
                {'error': 'No images provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        image_instances = []
        for image_data in images:
            image_instance = PostImage.objects.create(
                post=post,
                image=image_data,
                caption=request.data.get('caption', ''),
                order=PostImage.objects.filter(post=post).count()
            )
            image_instances.append(image_instance)
        
        serializer = PostImageSerializer(image_instances, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def react(self, request, slug=None):
        """Add or update a reaction (like/dislike) to a post"""
        post = self.get_object()
        user = request.user
        reaction_type = request.data.get('reaction_type')
        
        if reaction_type not in [Reaction.LIKE, Reaction.DISLIKE]:
            return Response(
                {'error': 'Invalid reaction type. Must be "like" or "dislike".'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user already reacted to this post
        try:
            reaction = Reaction.objects.get(post=post, user=user)
            # If the same reaction, remove it (toggle)
            if reaction.reaction_type == reaction_type:
                reaction.delete()
                return Response({'status': 'reaction removed'}, status=status.HTTP_200_OK)
            # Otherwise, update the reaction
            reaction.reaction_type = reaction_type
            reaction.save()
        except Reaction.DoesNotExist:
            # Create new reaction
            reaction = Reaction.objects.create(
                post=post,
                user=user,
                reaction_type=reaction_type
            )
        
        serializer = ReactionSerializer(reaction)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUserOrReadOnly]
    lookup_field = 'slug'

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    lookup_field = 'slug'

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    """
    API root endpoint showing available endpoints
    """
    return Response({
        'posts': request.build_absolute_uri('/api/posts/'),
        'categories': request.build_absolute_uri('/api/categories/'),
        'tags': request.build_absolute_uri('/api/tags/'),
        'register': request.build_absolute_uri('/api/register/'),
        'profile': request.build_absolute_uri('/api/profile/'),
        'token': request.build_absolute_uri('/api/token/'),
        'token_refresh': request.build_absolute_uri('/api/token/refresh/'),
    })

