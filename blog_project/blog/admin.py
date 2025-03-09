from django.contrib import admin
from .models import Post, Category, Tag, PostImage, Reaction

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'updated_at', 'published')
    list_filter = ('published', 'created_at', 'categories', 'tags')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    filter_horizontal = ('categories', 'tags')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [PostImageInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'content', 'excerpt', 'featured_image')
        }),
        ('Categorization', {
            'fields': ('categories', 'tags')
        }),
        ('Publication', {
            'fields': ('published', 'created_at', 'updated_at')
        }),
    )

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

class ReactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'reaction_type', 'created_at')
    list_filter = ('reaction_type', 'created_at')
    search_fields = ('user__username', 'post__title')
    date_hierarchy = 'created_at'

# Register models
admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(PostImage)
admin.site.register(Reaction, ReactionAdmin)

