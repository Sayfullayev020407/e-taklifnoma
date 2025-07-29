from django.contrib.auth.models import User
from django.db import models
from django.utils.crypto import get_random_string
from django.core.exceptions import ValidationError

class TelegramUser(models.Model):
    username = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    telegram_id = models.CharField(max_length=150, null=True, blank=True)
    profile_photo = models.ImageField(upload_to='profiles', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    
    def __str__(self) -> str:
        return self.username
        
    class Meta:
        verbose_name = 'Telegram Foydalanuvchi'
        verbose_name_plural = 'Telegram Foydalanuvchilar'

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category_image = models.ImageField(upload_to='categories', null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Kategoriya'
        verbose_name_plural = 'Kategoriyalar'

class BackgroundImage(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='backgrounds')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Fon rasmi'
        verbose_name_plural = 'Fon rasmlari'

class Invitation(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    background = models.ForeignKey(BackgroundImage, on_delete=models.SET_NULL, null=True)
    name_1 = models.CharField(max_length=100)
    name_2 = models.CharField(max_length=100, blank=True)
    date = models.DateTimeField()
    wedding_hall = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    apartment = models.CharField(max_length=100, null=True, blank=True)
    unique_url = models.CharField(max_length=100, unique=True)

    def generate_unique_url(self):
        """Generate a unique URL, retrying if a collision occurs."""
        max_attempts = 10
        length = 20  # Consistent length for unique_url
        for _ in range(max_attempts):
            unique_url = get_random_string(length)
            if not Invitation.objects.filter(unique_url=unique_url).exists():
                return unique_url
        raise ValidationError("Unable to generate a unique URL after multiple attempts.")

    def save(self, *args, **kwargs):
        if not self.unique_url:
            self.unique_url = self.generate_unique_url()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name_1}ning {self.category.name} to'yi"

    class Meta:
        verbose_name = 'Taklifnoma'
        verbose_name_plural = 'Taklifnomalar'