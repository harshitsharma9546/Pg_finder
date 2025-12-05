from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from pgs.models import PgListing, PGImage
from contact.models import ContactMessage

def home(request):
    pg_listings = PgListing.objects.filter(owner__is_owner=True)
    pg_images = PGImage.objects.all()
    context = {
        'pg_listings': pg_listings,
        'pg_images': pg_images,
    }

    return render(request, 'home.html', context)


def about(request):
    """Render the About page with full website information."""
    info = {
        'title': 'About PG Finder',
        'description': (
            'PG Finder (E-Hostel & PG) is a platform to connect clients looking for paying-guest ' 
            'accommodation with property owners. Our goal is to simplify PG search, listing, and ' 
            'management by providing an easy-to-use interface, secure user accounts, and built-in ' 
            'communication tools.'
        ),
        'features': [
            'Search PG listings by city, price and amenities',
            'Owners can register and list their PGs with images and specifications',
            'Clients can register, browse listings, and contact owners',
            'Email verification and password reset flows (development prints to console)',
            'Secure authentication and profile management',
        ],
        'how_it_works': [
            'Create an account as a client or an owner',
            'Owners add PG listings with details and photos',
            'Clients browse listings, view specifications, and contact owners',
            'Use the dashboard to manage listings and bookings (owner)',
        ],
        'privacy': (
            'We use your data to provide and improve the service. Sensitive information like ' 
            'Aadhar is stored only when explicitly provided by owners and should be handled with care. ' 
            'Do not share credentials or private data publicly.'
        ),
        'contact': {
            'email': 'support@example.com',
            'note': 'For feature requests or support, email us. Do not include passwords in email.'
        }
    }
    return render(request, 'about.html', info)


def contact(request):
    """Render contact page and handle form POST (sends email to support in DEBUG via console)."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_text = request.POST.get('message', '').strip()

        # Save to database
        try:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message_text,
            )
        except Exception:
            # Log/ignore save errors but still attempt to send
            pass

        # default subject if none provided
        if not subject:
            subject = f"Inquiry from {name or email}"

        full_message = f"From: {name} <{email}>\n\n{message_text}"

        # send to both support address shown on page and direct recipient
        recipients = ['harshtheking94@gmail.com', 'harshtheking04@gmail.com']
        # send message to support recipients
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com')
        sent_ok = False
        try:
            EmailMessage(subject, full_message, from_email=from_email, to=recipients).send()
            sent_ok = True
        except Exception:
            sent_ok = False

        # send acknowledgement to the submitter (if they provided an email)
        if email:
            try:
                ack_subject = f"We've received your message: {subject}"
                ack_body = (
                    f"Hi {name or ''},\n\n"
                    "Thanks for contacting PG Finder. We've received your inquiry and will reply soon. "
                    "Below is a copy of your message:\n\n"
                    f"{message_text}\n\n"
                    "— PG Finder Team"
                )
                EmailMessage(ack_subject, ack_body, from_email=from_email, to=[email]).send()
            except Exception:
                # ignore ack send failures
                pass

        if sent_ok:
            messages.success(request, 'Thanks — your message has been sent. We will reply soon.')
            return redirect('contact')
        else:
            messages.error(request, 'Failed to send message to support email. Please try again later.')

    # GET or failed POST
    return render(request, 'contact.html')