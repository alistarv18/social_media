from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from itertools import chain
from .models import Profile, Post, LikePost, FollowersCount
import random


# Create your views here.

@login_required(login_url='signin')
def index(request):
   # Obține profilul utilizatorului curent
   user_object = User.objects.get(username=request.user.username)
   user_profile = Profile.objects.filter(user=user_object).first()

   # Obține lista de utilizatori urmăriți
   user_following = FollowersCount.objects.filter(follower=request.user.username)
   user_following_list = [user.user for user in user_following]

   # Creează feed-ul de postări doar pentru utilizatorii urmăriți
   feed = Post.objects.filter(user__in=user_following_list)
   feed_list = list(feed)

   # Sugestii de utilizatori
   all_users = User.objects.exclude(username=request.user.username)  # Exclude utilizatorul curent
   user_following_all = User.objects.filter(username__in=user_following_list)  # Utilizatorii urmăriți
   suggestions = all_users.exclude(username__in=user_following_list)  # Exclude utilizatorii urmăriți

   # Selectează profilurile pentru sugestii
   suggestions_profiles = Profile.objects.filter(user__in=suggestions).distinct()

   # Amestecă sugestiile și returnează doar primele 4
   suggestions_profiles = list(suggestions_profiles)
   random.shuffle(suggestions_profiles)

   return render(request, 'index.html', {
      'user_profile': user_profile,
      'posts': feed_list,
      'suggestions_username_profile_list': suggestions_profiles[:4]
   })

@login_required(login_url='signin')
def upload(request):
   if request.method == 'POST':
      user = request.user.username
      image = request.FILES.get('image_upload')
      caption = request.POST['caption']

      new_post = Post.objects.create(user=user,image=image,caption=caption)
      new_post.save()

      return redirect('/')
   else:
      return redirect('/')

@login_required(login_url='signin')
def search(request):
   # Obține obiectele utilizatorului conectat
   user_object = User.objects.get(username=request.user.username)
   user_profile = Profile.objects.filter(user=user_object).first()

   # Inițializează lista profilelor pentru rezultate
   username_profile_list = []

   if request.method == "POST":
      username = request.POST.get('username', '').strip()  # Obține username-ul căutat

      if username:  # Asigură-te că username-ul nu este gol
         # Găsește utilizatorii care se potrivesc cu termenul căutat
         username_object = User.objects.filter(username__icontains=username)

         # Găsește profilele asociate utilizatorilor
         for user in username_object:
            profile_lists = Profile.objects.filter(user=user)
            username_profile_list.append(profile_lists)

         # Combină toate profilele într-o singură listă
         username_profile_list = list(chain.from_iterable(username_profile_list))

   return render(request, 'search.html', {
      'user_profile': user_profile,
      'username_profile_list': username_profile_list
   })

@login_required(login_url='signin')
def like_post(request):
   username = request.user.username
   post_id = request.GET.get('post_id')

   post = Post.objects.get(id=post_id)

   like_filter = LikePost.objects.filter(post_id=post_id,username=username).first()

   if like_filter is None:
      new_like=LikePost.objects.create(post_id=post_id,username=username)
      new_like.save()
      post.no_of_likes = post.no_of_likes+1
      post.save()
      return redirect('/')
   else:
      like_filter.delete()
      post.no_of_likes = post.no_of_likes -1
      post.save()
      return redirect('/')

@login_required(login_url='signin')
def profile(request,pk):
   user_object = User.objects.get(username=pk)
   user_profile = Profile.objects.get(user=user_object)
   user_posts = Post.objects.filter(user=pk)
   user_post_length = len(user_posts)

   follower = request.user.username
   user=pk
   if FollowersCount.objects.filter(follower=follower,user=user).first():
      button_text = "Unfollow"
   else:
      button_text = "Follow"

   user_followers = FollowersCount.objects.filter(user=pk).count()
   user_following = FollowersCount.objects.filter(follower=pk).count()

   context ={
      'user_object':user_object,
      'user_profile': user_profile,
      'user_posts': user_posts,
      'user_post_length': user_post_length,
      'button_text':button_text,
      'user_followers':user_followers,
      'user_following':user_following,
   }
   return render(request,'profile.html',context)

@login_required(login_url='signin')
def follow(request):
   if request.method == 'POST':
      follower = request.POST['follower']
      user = request.POST['user']

      if FollowersCount.objects.filter(follower=follower,user=user).first():
         delete_follower = FollowersCount.objects.get(follower=follower,user=user)
         delete_follower.delete()
         return redirect('/profile/'+user)
      else:
         new_follower = FollowersCount.objects.create(follower=follower,user=user)
         new_follower.save()
         return redirect('/profile/' + user)
   else:
      return redirect('/')

@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
       bio = request.POST.get('bio', '')  # Provide a default value (e.g., an empty string)
       location = request.POST.get('location', '')
       image = request.FILES.get('image', None)

       if bio or location or image:  # Update only if there is input
          user_profile.bio = bio
          user_profile.location = location

          if image:
             user_profile.profileimg = image

          user_profile.save()
       return redirect('settings')

    return render(request,'setting.html',{'user_profile': user_profile})
    #return render(request, 'setting.html')

def signup(request):
   if request.method=="POST": #procesarea datelor din form
      username = request.POST['username']
      email = request.POST['email']
      password = request.POST['password']
      password2 = request.POST['password2']

      if password == password2:
         if User.objects.filter(email=email).exists():
            messages.info(request,'Email taken')
            return redirect('signup')
            # se face redirect catre path-ul din urls.py
         elif User.objects.filter(username=username).exists():
            messages.info(request, 'Username taken')
            return redirect('signup')
         else:
            user = User.objects.create_user(username=username,email=email,password=password)
            user.save()

             #lLog user in and redirect to settings
            user_login = auth.authenticate(username=username,password=password)
            auth.login(request, user_login)

             #create a profile object for the new user
            user_model = User.objects.get(username=username)
            new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
            new_profile.save()
            return redirect('signup')
      else:
         messages.info(request,'Password not matching')
         return redirect('signup')

   else:
      #return redirect('signup')
      return render(request,'signup.html')


def signin(request):

   if request.method == 'POST':
      username = request.POST['username']
      password = request.POST['password']

      user = auth.authenticate(username=username,password=password)

      if user is not None:
         auth.login(request, user)
         return redirect('/')
      else:
         messages.info(request,'Credentials invalid')
         return redirect('signin')
   else:
      return render(request,'signin.html')

@login_required(login_url='signin')
def logout(request):
   auth.logout(request)
   return redirect('signin')
