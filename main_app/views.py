# at top of file with other imports
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.views import View
from .models import Artist, Song, Playlist
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView
from django.urls import reverse
# Auth
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


#...
# import models

# Create your views here.

# Here we will be creating a class called Home and extending it from the View class
class Home(TemplateView):
    template_name = "home.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["playlists"] = Playlist.objects.all()
        return context



class About(TemplateView):
    template_name = "about.html"


@method_decorator(login_required, name='dispatch')
class ArtistList(TemplateView):
    template_name = "artist_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        name = self.request.GET.get("name")
        # If a query exists we will filter by name 
        print(name)
        if name != None:
            # .filter is the sql WHERE statement and name__icontains is doing a search for any name that contains the query param
            context["artists"] = Artist.objects.filter(name__icontains=name)
            context["header"] = f"Searching through Artists list for {name}"
        else:
            context["artists"] = Artist.objects.all()
            context["header"] = "Trending Artists"
        return context
            # to show only users artists
        # if name != None:
        #     context["artists"] = Artist.objects.filter(
        #         name__icontains=name, user=self.request.user)
        #     context["header"] = f"Searching for {name}"
        # else:
        #     context["artists"] = Artist.objects.filter(user=self.request.user)
        #     context["header"] = "Trending Artists"
        # return context

class ArtistCreate(CreateView):
    model = Artist
    fields = ['name', 'img', 'bio', 'verified_artist']
    template_name = "artist_create.html"
    success_url = "/artists/"

    # This is our new method that will add the user into our submitted form
    # def form_valid(self, form):
        # example in js
       # # form.instance = {
       # #     name: name,
       # #     img: url,
       # #     bio: some string,
       # #     use: self.request.user
       # # }
    #     form.instance.user = self.request.user
    #     return super(ArtistCreate, self).form_valid(form)

    # def get_success_url(self):
    #     print(self.kwargs)
    #     return reverse('artist_detail', kwargs={'pk': self.object.pk})

class ArtistDetail(DetailView):
    model = Artist
    template_name = "artist_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["playlists"] = Playlist.objects.all()
        return context

class ArtistUpdate(UpdateView):
    model = Artist
    fields = ['name', 'img', 'bio', 'verified_artist']
    template_name = "artist_update.html"
    success_url = "/artists/"


class ArtistDelete(DeleteView):
    model = Artist
    template_name = "artist_delete_confirmation.html"
    success_url = "/artists/"


class SongCreate(View):

    def post(self, request, pk):
        title = request.POST.get("title")
        minutes = request.POST.get("minutes")
        seconds = request.POST.get("seconds")
        formLength = 60 * int(minutes) + int(seconds)
        artist = Artist.objects.get(pk=pk)
        Song.objects.create(title=title, length=formLength, artist=artist)
        return redirect('artist_detail', pk=pk)


class PlaylistSongAssoc(View):

    def get(self, request, pk, song_pk):
        # get the query param from the url
        assoc = request.GET.get("assoc")
        if assoc == "remove":
            # get the playlist by the id and
            # remove from the join table the given song_id
            Playlist.objects.get(pk=pk).songs.remove(song_pk)
        if assoc == "add":
            # get the playlist by the id and
            # add to the join table the given song_id
            Playlist.objects.get(pk=pk).songs.add(song_pk)
        return redirect('home')


class Signup(View):
    # show a form to fill out
    def get(self, request):
        form = UserCreationForm()
        context = {"form": form}
        return render(request, "registration/signup.html", context)
    # on form submit, validate the form and login the user.
    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("artist_list")
        else:
            context = {"form": form}
            return render(request, "registration/signup.html", context)
