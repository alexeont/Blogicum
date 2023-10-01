from django.contrib import admin

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


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'post_id',
        'created_at',
        'author',
    )

    search_fields = list_display
    list_filter = list_display
