from django.shortcuts import redirect, render
from django.http import Http404
from .models import PgListing, Booking
from users.models import MyUser
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from decimal import Decimal, InvalidOperation
from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
import math
import qrcode
import io
from django.core.files.base import ContentFile
import urllib.parse

# PhonePe UPI ID (Change this to your actual PhonePe UPI)
PHONEPE_UPI = "9876543210@ybl"  # Example UPI ID

# Create QR Code for PhonePe Payment
def generate_phonepe_qr_code(booking):
    """Generate PhonePe payment QR code with UPI deep link"""
    # PhonePe UPI format: upi://pay?pa=UPI_ID&pn=NAME&am=AMOUNT&tn=DESCRIPTION
    amount_in_rupees = str(booking.amount)
    pg_name = booking.pg.title[:20]  # Limit name length
    description = f"PG Booking #{booking.id}"
    
    # Create UPI string
    upi_string = f"upi://pay?pa={PHONEPE_UPI}&pn={urllib.parse.quote(pg_name)}&am={amount_in_rupees}&tn={urllib.parse.quote(description)}"
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(upi_string)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR code to file
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    filename = f"qr_phonepe_{booking.id}.png"
    booking.qr_code.save(filename, ContentFile(buffer.read()), save=True)
    booking.phonepe_upi = PHONEPE_UPI
    booking.save()
    
    return booking

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

@login_required(login_url='user_login')
def book_pg(request, pg_slug):
    try:
        pg = PgListing.objects.get(slug=pg_slug)
    except PgListing.DoesNotExist:
        raise Http404('PG not found')
    
    if request.method == 'POST':
        check_in_date_str = request.POST.get('check_in_date')
        visit_later = request.POST.get('visit_later', False)
        
        # Check if user already has a booking for this PG
        existing_booking = Booking.objects.filter(
            tenant=request.user,
            pg=pg,
            status__in=['pending', 'confirmed']
        ).first()
        
        if existing_booking:
            messages.error(request, 'You already have an active booking for this PG!')
            return redirect('pg_detail', pg_slug=pg_slug)
        
        # Create booking
        booking = Booking.objects.create(
            tenant=request.user,
            pg=pg,
            check_in_date=timezone.now().date() if not check_in_date_str else check_in_date_str,
            amount=pg.price_per_month,
            visit_later=visit_later,
            status='pending'
        )
        
        # Generate PhonePe QR code
        booking = generate_phonepe_qr_code(booking)
        
        messages.success(request, 'Booking created successfully!')
        return redirect('booking_confirmation', booking_id=booking.id)
    
    return redirect('pg_detail', pg_slug=pg_slug)

@login_required(login_url='user_login')
def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, tenant=request.user)
    
    context = {
        'booking': booking,
        'pg': booking.pg,
        'qr_code_url': booking.qr_code.url if booking.qr_code else None,
    }
    return render(request, 'pgs/booking_confirmation.html', context)

@login_required(login_url='user_login')
def confirm_payment(request, booking_id):
    """Mark booking as confirmed after payment"""
    booking = get_object_or_404(Booking, id=booking_id, tenant=request.user)
    
    if request.method == 'POST':
        booking.status = 'confirmed'
        booking.payment_confirmed_date = timezone.now()
        booking.save()
        messages.success(request, 'Payment confirmed! Your booking is now active.')
        return redirect('my_bookings_list')
    
    return render(request, 'pgs/confirm_payment.html', {'booking': booking})

@login_required(login_url='user_login')
def my_bookings_list(request):
    bookings = Booking.objects.filter(tenant=request.user).order_by('-booking_date')
    
    context = {
        'bookings': bookings,
    }
    return render(request, 'pgs/my_bookings_list.html', context)

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

def about(request):
    return render(request, "about.html")



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


@login_required(login_url='user_login')
def cancel_booking(request, booking_id):
    """Cancel a booking (marks status as 'cancelled')."""
    booking = get_object_or_404(Booking, id=booking_id, tenant=request.user)
    if request.method == 'POST':
        if booking.status == 'cancelled':
            messages.info(request, 'Booking already cancelled.')
        else:
            booking.status = 'cancelled'
            booking.save()
            messages.success(request, 'Booking cancelled successfully.')
    return redirect('my_bookings_list')
    

