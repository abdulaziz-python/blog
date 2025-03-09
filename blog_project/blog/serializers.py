from rest_framework import serializers
from .models import Post, Category, Tag, PostImage, Reaction
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']

class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['id', 'image', 'caption', 'order']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class ReactionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Reaction
        fields = ['id', 'user', 'reaction_type', 'created_at']
        read_only_fields = ['user', 'created_at']

class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    images = PostImageSerializer(many=True, read_only=True)
    rendered_content = serializers.ReadOnlyField()
    likes_count = serializers.ReadOnlyField()
    dislikes_count = serializers.ReadOnlyField()
    category_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        write_only=True,
        queryset=Category.objects.all(),
        source='categories',
        required=False
    )
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        write_only=True,
        queryset=Tag.objects.all(),
        source='tags',
        required=False
    )
    user_reaction = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'content', 'rendered_content', 'excerpt',
            'author', 'featured_image', 'categories', 'tags', 'images',
            'created_at', 'updated_at', 'published', 'category_ids', 'tag_ids',
            'likes_count', 'dislikes_count', 'user_reaction'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at', 'slug', 'rendered_content']
    
    def get_user_reaction(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                reaction = Reaction.objects.get(post=obj, user=request.user)
                return reaction.reaction_type
            except Reaction.DoesNotExist:
                return None
        return None

class PostDetailSerializer(PostSerializer):
    """Serializer for detailed post view with all fields"""
    reactions = ReactionSerializer(many=True, read_only=True)
    
    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ['reactions']

class PostListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    author = serializers.ReadOnlyField(source='author.username')
    categories = serializers.StringRelatedField(many=True)
    tags = serializers.StringRelatedField(many=True)
    likes_count = serializers.ReadOnlyField()
    dislikes_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'excerpt', 'author', 
            'featured_image', 'categories', 'tags',
            'created_at', 'updated_at', 'published',
            'likes_count', 'dislikes_count'
        ]

class PostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating posts via API"""
    category_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        write_only=True,
        queryset=Category.objects.all(),
        source='categories',
        required=False
    )
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        write_only=True,
        queryset=Tag.objects.all(),
        source='tags',
        required=False
    )
    
    class Meta:
        model = Post
        fields = [
            'title', 'content', 'excerpt', 'featured_image',
            'category_ids', 'tag_ids', 'published'
        ]

