from django.shortcuts import render,redirect
from django.http import HttpResponse
from pgs.models import PgListing, PGImage

def home(request):
    pg_listings = PgListing.objects.filter(owner__is_owner=True)
    pg_images = PGImage.objects.all()
    context = {
        'pg_listings': pg_listings,
        'pg_images': pg_images,
    }

    return render(request, 'home.html', context)