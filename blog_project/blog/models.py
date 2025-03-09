import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import markdown
from django.utils.html import mark_safe

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

def post_image_upload_path(instance, filename):
    # Generate a unique path for each uploaded image
    return f'blog/posts/{instance.slug}/{uuid.uuid4()}/{filename}'

class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=250)
    content = models.TextField(help_text="Content in Markdown format")
    excerpt = models.TextField(blank=True, help_text="Short description for previews")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    featured_image = models.ImageField(upload_to=post_image_upload_path, blank=True, null=True)
    categories = models.ManyToManyField(Category, blank=True, related_name='posts')
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.excerpt and self.content:
            # Create an excerpt from the first 150 characters of content
            plain_content = self.content.replace('#', '').replace('*', '')
            self.excerpt = plain_content[:150] + '...' if len(plain_content) > 150 else plain_content
        super().save(*args, **kwargs)
    
    @property
    def rendered_content(self):
        """Convert markdown content to HTML"""
        return mark_safe(markdown.markdown(
            self.content,
            extensions=['markdown.extensions.fenced_code', 
                        'markdown.extensions.tables',
                        'markdown.extensions.nl2br']
        ))
    
    @property
    def likes_count(self):
        return self.reactions.filter(reaction_type=Reaction.LIKE).count()
    
    @property
    def dislikes_count(self):
        return self.reactions.filter(reaction_type=Reaction.DISLIKE).count()

def post_attachment_upload_path(instance, filename):
    # Generate a unique path for each uploaded attachment
    return f'blog/posts/{instance.post.slug}/attachments/{uuid.uuid4()}/{filename}'

class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=post_attachment_upload_path)
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Image for {self.post.title}"

class Reaction(models.Model):
    LIKE = 'like'
    DISLIKE = 'dislike'
    
    REACTION_CHOICES = [
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
    ]
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['post', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} {self.reaction_type}d {self.post.title}"

