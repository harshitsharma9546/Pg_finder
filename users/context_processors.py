from pgs.models import Booking


def booking_counts(request):
    """Inject pending and confirmed booking counts for the authenticated user."""
    pending = 0
    confirmed = 0
    user = getattr(request, 'user', None)
    if user and user.is_authenticated:
        pending = Booking.objects.filter(tenant=user, status='pending').count()
        confirmed = Booking.objects.filter(tenant=user, status='confirmed').count()
    return {
        'pending_bookings_count': pending,
        'confirmed_bookings_count': confirmed,
    }
