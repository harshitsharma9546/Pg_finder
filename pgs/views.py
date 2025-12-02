from django.shortcuts import redirect, render
from django.http import Http404
from .models import PgListing
from users.models import MyUser
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from decimal import Decimal, InvalidOperation
from django.shortcuts import get_object_or_404, render
import math

# Create your views here.
@login_required(login_url='user_login')
def pg_detail(request, pg_slug):
    try:
        pg = PgListing.objects.get(slug=pg_slug)
    except PgListing.DoesNotExist:
        raise Http404('PG not found') 
    owner = pg.owner
    OFF_PERCENT = 37
    price_raw = getattr(pg, 'price_per_month', 0) or 0
    try:
        price_dec = Decimal(str(price_raw))
        mrp_dec = price_dec / (Decimal(1) - (Decimal(OFF_PERCENT) / Decimal(100)))
        mrp = int(math.ceil(mrp_dec))
    except (InvalidOperation, TypeError, ZeroDivisionError):
        # fallback: use price as mrp if something goes wrong
        try:
            mrp = int(price_raw)
        except Exception:
            mrp = 0
        price_dec = Decimal(str(mrp))

    show_mrp = mrp > int(price_dec)

    context = {
        'pg': pg,
        'mrp': mrp,
        'off': OFF_PERCENT,
        'show_mrp': show_mrp,
    }
    return render(request, 'pgs/pg-specification.html', context)

def search(request):
    query = request.GET.get('keyword')
    if query:
        pgs = PgListing.objects.filter(owner__is_owner=True).filter(title__icontains=query) | PgListing.objects.filter(owner__is_owner=True).filter(city__icontains=query) | PgListing.objects.filter(owner__is_owner=True).filter(state__icontains=query)
    else:
        pgs = PgListing.objects.none()
    context = {
        'pgs': pgs,
        # 'query': query
    }
    return render(request, 'pgs/pgs.html', context)


def pgs(request):
    pgs = PgListing.objects.filter(owner__is_owner=True)
    context = {
        'pgs': pgs
    }
    return render(request, 'pgs/pgs.html', context)


@login_required(login_url='user_login') 
def pg_register(request):
    if not request.user.is_owner:
        return redirect('home')  
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pin_code = request.POST.get('pin_code')
        price_per_month = request.POST.get('price_per_month')
        available_from = request.POST.get('available_from')
        type_of_pg = request.POST.get('type_of_pg')
        amenities = request.POST.get('amenities')
        sharing_type = request.POST.get('sharing_type')
        pg_images = request.FILES.getlist('pg_images')
        
        owner = request.user 

        slug = slugify(title)
        # Ensure slug is unique
        base_slug = slug
        counter = 1
        while PgListing.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
            
        # Create a new PgListing instance
        pg_listing = PgListing.objects.create(
            owner=owner,
            title=title,
            slug=slug,
            description=description,
            address=address,
            city=city,
            state=state,
            pin_code=pin_code,
            price_per_month=price_per_month,
            available_from=available_from,
            type_of_pg=type_of_pg,
            amenities=amenities,
            sharing_type=sharing_type
        )
        # Save the images
        for image in pg_images:
            pg_listing.images.create(pg_image=image)
        
        return redirect('pgs')  # Redirect to a success page or the PG listing page
    else:   
        return render(request, 'users/owners/pgregister.html')
    

