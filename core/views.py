from ast import Try
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import profileForm
from .models import Movie, Profile, WatchaMovie, WatchaUser, WatchaRating

from .surprise import Surprise_KNNBaseline
import pandas as pd

# Create your views here.

# class Surprise(View):
#     def get(self,request):
#         ratings = pd.read_csv('./data/watcha_ratings.csv', encoding = 'utf-8')
#         movies = pd.read_csv('./data/watcha_movies.csv', encoding = 'utf-8')
#         users = pd.read_csv('./data/watcha_users.csv', encoding = 'utf-8')
        
#         recomm_1765 = Surprise_KNNBaseline(ratings, movies, users,1765, n = 30)
    
#         recomm_list = []
#         for item in recomm_1765.values:
#             recomm_list.append(list(item))

#         context = {'ratings':ratings.to_html,'recomm_1765':recomm_1765.to_html,'recomm_list':recomm_list}
#         return render(request,'watchamovie.html',context)

@method_decorator(login_required,name='dispatch')
class Watcha(View):
    def get(self,request,*args, **kwargs): 
        email = request.user.email
        watchauser=WatchaUser.objects.get(user_email=email)
        watcharating=WatchaRating.objects.filter(user_index=watchauser.user_index)

        movie_list = []
        for item in watcharating:
            selected_movie = WatchaMovie.objects.get(movie_index=item.movie_index)
            movie_list.append(selected_movie)

        ratings = pd.read_csv('./data/watcha_ratings.csv', encoding = 'utf-8')
        movies = pd.read_csv('./data/watcha_movies.csv', encoding = 'utf-8')
        users = pd.read_csv('./data/watcha_users.csv', encoding = 'utf-8')
        recomm_1765 = Surprise_KNNBaseline(ratings, movies, users,0, n = 30)
    
        recomm_list = []
        for item in recomm_1765.values:
            recomm_list.append(list(item)[0])

        context = {'watchauser':watchauser, 'watcharating':watcharating, 'movie_list':movie_list[:10], 'email':email,'ratings':ratings.to_html,
        'recomm_list':recomm_list[:10]}

        return render(request,'watchamovie.html',context)





class Home(View):
    def get(self,request,*args,**kwargs):
        if request.user.is_authenticated:
            return redirect('core:profile_list')
        return render(request,'index.html')


# ????????? ????????? ?????? ????????? ??????????????? ??????????????? ?????? decorator ??? ????????? ????????? ??? ??? ??? ????????????.
@method_decorator(login_required,name='dispatch') # https://ssungkang.tistory.com/entry/Django-FBV-???-CBV-???-decorators-?????????
class ProfileList(View):
    def get(self,request,*args,**kwargs):
        profiles=request.user.profiles.all()
        return render(request,'profileList.html',{
            'profiles':profiles
        })



@method_decorator(login_required,name='dispatch')
class ProfileCreate(View):
    def get(self,request,*args, **kwargs):
        # form for creating profile
        form=profileForm()

        return render(request,'profileCreate.html',{
            'form':form
        })

    def post(self,request,*args, **kwargs):
        form=profileForm(request.POST or None)

        if form.is_valid():
            # print(form.cleaned_data)
            profile = Profile.objects.create(**form.cleaned_data)
            if profile:
                request.user.profiles.add(profile)
                return redirect('core:profile_list')
        
        return render(request,'profileCreate.html',{
            'form':form
        })


@method_decorator(login_required,name='dispatch')
class Watch(View):
    def get(self,request,profile_id,*args, **kwargs):
        try:
            profile=Profile.objects.get(uuid=profile_id)
            movies=Movie.objects.filter(age_limit=profile.age_limit)
            watchamovie=WatchaMovie.objects.all()    
            context = {'movies':movies, 'watchamovie': watchamovie}

            if profile not in request.user.profiles.all():
                return redirect(to='core:profile_list')
            
            return render(request,'movieList.html',context)
        except Profile.DoesNotExist:
            return redirect(to='core:profile_list')


@method_decorator(login_required,name='dispatch')
class ShowMovieDetail(View):
    def get(self,request,movie_id,*args, **kwargs):
        try:
            movie=Movie.objects.get(uuid=movie_id)

            return render(request,'movieDetail.html',{
                'movie':movie
            })
        except Movie.DoesNotExist:
            return redirect('core:profile_list')


@method_decorator(login_required,name='dispatch')
class ShowMovie(View):
    def get(self, request, movie_id, *args, **kwargs):
        try:
            movie=Movie.objects.get(uuid=movie_id)
            movie=movie.videos.values()

            return render(request,'showMovie.html',{
                'movie':list(movie)
            })

        except Movie.DoesNotExist:
            return redirect('core:profile_list')


#=====================================================================