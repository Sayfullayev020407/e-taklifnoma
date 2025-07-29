from django.contrib import admin
from .models import TelegramUser, Category, BackgroundImage, Invitation

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'telegram_id')
    search_fields = ('username', 'telegram_id')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(BackgroundImage)
class BackgroundImageAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'name_1', 'name_2', 'date')
    search_fields = ('name_1', 'name_2', 'unique_url')
    list_filter = ('category',)