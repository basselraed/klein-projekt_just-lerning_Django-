from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login , logout
from django.db.models import Q 
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .forms import RoomForm

# rooms=[
#    {'room_id':1,'room_name':'the first Room/website'},
#     {'room_id':2,'room_name':'the second Room/website'},
#     {'room_id':3,'room_name':'the third Room/website'},
# ]

# view for logging a User und getting the the User information from a Post methode  and checking if the User is authenticated or not  if Not then we have  a flsche message []
def loginPage(request):
    page='login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username=request.POST.get('username').lower()
        password=request.POST.get('password')
        try:
            user= User.objects.get(username=username)
        except:
           messages.error(request,'User does not exist')

        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'Username OR Password is incorrect')
            

    context={'page': page}
    return render(request,'base/login_register.html',context)

# a view for the logout a User und riedeircting him  in the home page
def logoutUser(request):
    logout(request)
    return redirect('home')

#creat a registerPage
def registerPage(request):
    form=  UserCreationForm()
    if request.method == 'POST':
        form= UserCreationForm(request.POST)
        if form.is_valid():
            user =form.save(commit=False)
            user.username=user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request, 'an error occurred while registering')
    return render(request,'base/login_register.html',{ 'form': form})

#  a view for the home page
def home(request):
    q=request.GET.get('q') if request.GET.get('q')!= None else ''
    rooms = Room.objects.filter( 
    Q ( topic__name__icontains=q) | Q (name__icontains=q) | Q (description__icontains=q) 
    )
    topics =Topic.objects.all()
    room_count = rooms.count()
    room_messages=Message.objects.filter(Q(room__topic__name__icontains=q))
    context={'rooms':rooms ,'topics':topics ,'room_count':room_count ,'room_messages':room_messages}
    return render(request,'base/home.html',context)

# a function that defines the rooms .
def room(request,pk):
    room=Room.objects.get(id=pk)
    room_messages=room.message_set.all()
    participants=room.participants.all()
    
    if request.method=='POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room',pk=room.id)
    context={'room':room ,'room_messages':room_messages ,'participants':participants}
    return render(request,'base/room.html',context)

# a userprofile view 
def userProfile(request,pk):
    user=User.objects.get(id=pk)
    romms=user.room_set.all()
    room_messages=user.message_set.all()
    topics=Topic.objects.all()
    context={'user':user ,'romms':romms ,'room_messages':room_messages ,'topics':topics}
    return render(request,'base/profile.html',context)

# redirect the user to the login page ,when he not logged and want to create a new room
@login_required(login_url='login')
def createRoom(request):
    form=RoomForm()
    if request.method=='POST':
        form=RoomForm(request.POST)
        if form.is_valid():
            room=form.save()
            room.host=request.user
            room.save()
            return redirect('home')
    context={'form':form}
    return render(request,'base/room_form.html',context)

# aview for updating a room 
@login_required(login_url='login')
def updateRoom(request,pk):
    room=Room.objects.get(id=pk)
    form=RoomForm(instance=room)
    if request.user!=room.host:
        return HttpResponse(' your are not allowed to be hiere to update')
    if request.method=='POST':
        form=RoomForm(request.POST,instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    context={'form':form}
    return render(request,'base/room_form.html',context)

# a view for deleting a room
@login_required(login_url='login')
def deleteRoom(request,pk):
    room=Room.objects.get(id=pk)
    if request.user!=room.host:
        return HttpResponse(' your are not allowed to be hiere to update')
    if request.method=='POST':
        room.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':room})    

# a view for deleting a room
@login_required(login_url='login')
def deleteMessage(request,pk):
    message=Message.objects.get(id=pk)
    if request.user!=message.user:
        return HttpResponse(' your are not allowed to be hiere to update')
    if request.method=='POST':
        message.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':message}) 