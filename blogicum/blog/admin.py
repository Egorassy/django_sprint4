# admin.py
from django.contrib import admin
from .models import Category, Location, Post, Comment


class CustomAdminMixin:
    class Media:
        css = {
            'all': ('css/style.css',)
        }


@admin.register(Category)
class CategoryAdmin(CustomAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'is_published', 'created_at')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Location)
class LocationAdmin(CustomAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'is_published', 'created_at')


@admin.register(Post)
class PostAdmin(CustomAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'pub_date', 'is_published')
    list_filter = ('is_published', 'category', 'author')
    search_fields = ('title', 'text')
    raw_id_fields = ('author', 'category', 'location')


@admin.register(Comment)
class CommentAdmin(CustomAdminMixin, admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at')
    search_fields = ('text',)
    raw_id_fields = ('post', 'author')
