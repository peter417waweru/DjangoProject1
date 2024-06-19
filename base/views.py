from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Room, Topic, Message
from .forms import RoomForm

#rooms = [
#    {'id': 1, 'name': 'lets learn python!'},
#    {'id': 2, 'name': 'Design something with me!'},
#    {'id': 3, 'name': 'Front end developers!'},
#]

def LoginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
     
    if request.method == 'POST':
        username = request.POST.get('Username')
        password = request.POST.get('Password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "User does not exist.")
            return render(request, 'base/registration_login.html')

        user = authenticate(request, username=username, password=password) 

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
             messages.error(request, "Incorrect Username Or Password.")  
    context = {'page': page}
    return render(request, 'base/registration_login.html', context)

def LogoutPage(request):
    logout(request)
    return redirect('login')

def SignupPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "passwords do not match...")
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return redirect('signup')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect('signup')
        
        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()
            messages.success(request, f"Account for {username} created sucsessfuly.")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"An error occurred during account creation. Please try again. {str(e)}")

    return render(request, 'base/signup.html')

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
                                Q(topic__name__icontains=q) |
                                Q(name__icontains=q) |
                                Q(description__icontains=q)
                                )

    room_count = rooms.count()
    topics = Topic.objects.all()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains= q))


    context = {'rooms': rooms, 'topics': topics, 'room_count':room_count,
               'room_messages':room_messages}
    return render(request, 'base/home.html', context)

def room(request, pw):
    room = Room.objects.get(id=pw)
    participants = room.participants.all()
    room_messages = room.message_set.all()

    if request.method == 'POST':
        if request.user.is_authenticated:
             message_body=request.POST.get('body')
             Message.objects.create(
                user=request.user,
                room=room,
                body = message_body
            )
             room.participants.add(request.user)
             return redirect('room', pw=room.id)
        else:
            messages.error(request, "You Must login first!!.")
            return redirect('login')

    context = {'room': room, 'room_messages': room_messages, 'participants':participants}
    return render(request, 'base/room.html', context)

def userProfile(request, pw):
    user = User.objects.get(id=pw)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()

    context = {'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)

@login_required(login_url = '/login')
def createRoom(request):
    form = RoomForm

    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():

            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url = '/login')
def updateRoom(request, pw):
    room = Room.objects.get(id=pw)
    form = RoomForm(instance=room)

    if request.user != room.host:
        messages.error(request, "You are not authorized to update this room")
        return redirect('home')

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    

    context = {'form': form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url = '/login')
def deleteRoom(request, pw):
    room = Room.objects.get(id=pw)
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    
    room = get_object_or_404(Room, id=pw)

    if room.owner != request.user:
        messages.error(request, "You are not authorized to delete this room.")
        return redirect('home')

    return render(request, 'base/delete.html', {'obj':room})

@login_required(login_url = '/login')
def deleteMessage(request, pw):
    message = Message.objects.get(id=pw)
    room_id = message.room.id

    if request.user != message.user:
        messages.error(request, "You are not authorized to delete this Message.")
        return redirect('room', pw=room_id)


    if request.method == 'POST':
        message.delete()
        return redirect('room', pw=room_id)

    
    return render(request, 'base/delete.html', {'obj':message})
