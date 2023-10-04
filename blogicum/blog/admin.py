from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Category, Location, Post, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'slug',
        'is_published',
        'created_at'
    )
    list_editable = (
        'description',
        'is_published'
    )
    search_fields = ('title',)
    list_filter = ('is_published',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published',
        'created_at'
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('name',)
    list_filter = ('is_published',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
        'created_at',
        'image',
        'picture_display',
    )
    list_editable = (
        'is_published',
    )
    search_fields = (
        'title',
        'pub_date',
        'author',
        'location',
        'category'
    )
    list_filter = (
        'is_published',
        'pub_date',
        'author',
        'location',
        'category',
        'created_at'
    )

    def picture_display(self, obj):
        if obj.image:
            return mark_safe(f'(<img src={obj.image.url} width="80" height="60">')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'post',
        'created_at',
        'author',
    )

    search_fields = list_display
    list_filter = list_display
