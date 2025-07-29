from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import TelegramUser, Category, Invitation, BackgroundImage
import urllib.parse
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
import os
import io
import numpy as np
import telebot

def send_file_to_telegram(chat_id, file_path, file_type='photo'):
    bot = telebot.TeleBot('7262457869:AAGWaZENB2jkp1Gcaj5m4o_p1ELTuwX0wEg')
    try:
        with open(file_path, 'rb') as file:
            if file_type == 'photo':
                bot.send_photo(chat_id=chat_id, photo=file)
            elif file_type == 'video':
                bot.send_video(chat_id=chat_id, video=file)
        return True
    except Exception as e:
        print(f"Telegram send error: {e}")
        return False

def index(request):
    tg_id = request.GET.get('tg_id') or request.session.get('tg_id')
    username = request.GET.get('username') or request.session.get('username')
    first_name = request.GET.get('first_name') or request.session.get('first_name')
    last_name = request.GET.get('last_name') or request.session.get('last_name')
    profile_photo = request.GET.get('profile_photo') or request.session.get('profile_photo')

    if not tg_id or not username:
        return render(request, 'index.html', context={'message': 'Telegram maʼlumotlari yetishmayapti'})

    user = authenticate(request, username=tg_id, password=tg_id)

    if user is None:
        user = User.objects.create_user(username=tg_id, password=tg_id)

    tg_user, created = TelegramUser.objects.get_or_create(user=user)
    tg_user.username = username
    tg_user.first_name = first_name
    tg_user.last_name = last_name
    tg_user.telegram_id = tg_id

    if profile_photo:
        tg_user.profile_photo = urllib.parse.unquote(profile_photo) 
    tg_user.save()

    request.session['tg_id'] = tg_id
    request.session['username'] = username
    request.session['first_name'] = first_name
    request.session['last_name'] = last_name
    request.session['profile_photo'] = profile_photo

    login(request, user)
    categories = Category.objects.all()
    context = {
        'message': 'Tizimga kirdi' if not created else 'Yangi foydalanuvchi yaratildi',
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
        'telegram_id': tg_id,
        'profile_photo': tg_user.profile_photo,
        'categories': categories,
        'home':'home',
        'telegram_user': tg_user
    }
    return render(request, 'index.html', context)

@login_required
def create_invitation(request, category_id):
    telegram_user = TelegramUser.objects.get(user=request.user)
    category = get_object_or_404(Category, id=category_id)
    backgrounds = BackgroundImage.objects.all()
    if request.method == 'POST':
        try:
            name_1 = request.POST.get('name_1')
            name_2 = request.POST.get('name_2') if category.name == 'Nikoh' else ''
            date = request.POST.get('date')
            wedding_hall = request.POST.get('wedding_hall')
            address = request.POST.get('address')
            apartment = request.POST.get('apartment')
            background_id = request.POST.get('background')

            invitation = Invitation(
                user=TelegramUser.objects.get(user=request.user),
                category=category,
                background_id=background_id,
                name_1=name_1,
                name_2=name_2,
                date=date,
                wedding_hall=wedding_hall,
                address=address,
                apartment=apartment
            )
            invitation.save()
            return redirect('invitation_page', invitation.unique_url)
        except ValidationError as e:
            return render(request, 'create_invitation.html', {
                'category': category,
                'backgrounds': backgrounds,
                'error': str(e),
                'telegram_user': telegram_user
            })
    return render(request, 'create_invitation.html', {'category': category, 'backgrounds': backgrounds,'telegram_user': telegram_user})

@login_required
def my_invitations(request):
    telegram_user = TelegramUser.objects.get(user=request.user)
    invitations = Invitation.objects.filter(user__user=request.user)
    return render(request, 'my_invitations.html', {'invitations': invitations,'telegram_user': telegram_user})

@login_required
def invitation_detail(request, invitation_id):
    telegram_user = TelegramUser.objects.get(user=request.user)
    invitation = get_object_or_404(Invitation, id=invitation_id, user__user=request.user)
    return render(request, 'invitation_detail.html', {'invitation': invitation,'telegram_user': telegram_user})

@login_required
def edit_invitation(request, invitation_id):
    telegram_user = TelegramUser.objects.get(user=request.user)
    invitation = get_object_or_404(Invitation, id=invitation_id, user__user=request.user)
    backgrounds = BackgroundImage.objects.all()
    if request.method == 'POST':
        try:
            invitation.name_1 = request.POST.get('name_1')
            if invitation.category.name == 'Nikoh':
                invitation.name_2 = request.POST.get('name_2')
            invitation.date = request.POST.get('date')
            invitation.wedding_hall = request.POST.get('wedding_hall')
            invitation.address = request.POST.get('address')
            invitation.apartment = request.POST.get('apartment')
            invitation.background_id = request.POST.get('background')
            invitation.save()
            return redirect('my_invitations')
        except ValidationError as e:
            return render(request, 'edit_invitation.html', {
                'invitation': invitation,
                'backgrounds': backgrounds,
                'error': str(e)
            })
    return render(request, 'edit_invitation.html', {'invitation': invitation, 'backgrounds': backgrounds,'telegram_user': telegram_user})

@login_required
def delete_invitation(request, invitation_id):
    telegram_user = TelegramUser.objects.get(user=request.user)
    invitation = get_object_or_404(Invitation, id=invitation_id, user__user=request.user)
    if request.method == 'POST':
        invitation.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def invitation_page(request, unique_url):
    invitation = get_object_or_404(Invitation, unique_url=unique_url)
    share_url = request.build_absolute_uri()
    return render(request, 'invitation_page.html', {
        'invitation': invitation,
        'share_url': share_url
    })

@login_required
def send_image(request, invitation_id):
    telegram_user = TelegramUser.objects.get(user=request.user)
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    invitation = get_object_or_404(Invitation, id=invitation_id, user__user=request.user)
    telegram_user = TelegramUser.objects.get(user=request.user)
    
    # Create image
    background = Image.open(invitation.background.image.path)
    draw = ImageDraw.Draw(background)
    
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    text = f"{invitation.name_1}"
    if invitation.category.name == 'Nikoh' and invitation.name_2:
        text += f" va {invitation.name_2}"
    text += f"\n{invitation.category.name}\n"
    text += f"Sana: {invitation.date.strftime('%d.%m.%Y %H:%M')}\n"
    text += f"To'yxona: {invitation.wedding_hall}\n"
    text += f"Manzil: {invitation.address}"
    if invitation.apartment:
        text += f"\nXonadon: {invitation.apartment}"
    
    # Matnni markazga joylashtirish uchun koordinatalar
    img_width, img_height = background.size
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x_position = (img_width - text_width) // 2  # Markazga horizontal joylashtirish
    y_position = (img_height - text_height) // 2  # Markazga vertikal joylashtirish
    
    draw.text((x_position, y_position), text, fill=(255, 255, 255), font=font)
    
    temp_image_path = os.path.join(settings.MEDIA_ROOT, f'temp_{invitation.id}.png')
    background.save(temp_image_path)
    
    # Send to Telegram
    success = send_file_to_telegram(telegram_user.telegram_id, temp_image_path, 'photo')
    os.remove(temp_image_path)
    
    if success:
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Telegramga yuborishda xatolik'})

def profile(request):
    telegram_user = TelegramUser.objects.get(user=request.user)
    tg_user = TelegramUser.objects.get(user=request.user)
    return render(request, 'profile.html', {'profile': tg_user,'telegram_user': telegram_user})



