from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from .models import Page, NewsUpdate, ContactSubmission

# Set up logging
logger = logging.getLogger(__name__)


def about(request):
    """About page view"""
    from .models import ArtistEducation, ArtistAward, Exhibition, ArtistPublication
    
    try:
        about_page = Page.objects.get(page_type='about', is_published=True)
    except Page.DoesNotExist:
        about_page = None
    
    # Get artist education and credentials
    education_list = ArtistEducation.objects.all()
    awards_list = ArtistAward.objects.all()
    exhibitions_list = Exhibition.objects.filter(is_featured=True)[:6]  # Show featured exhibitions
    publications_list = ArtistPublication.objects.all()[:5]  # Show recent 5 publications
    
    context = {
        'page': about_page,
        'education_list': education_list,
        'awards_list': awards_list,
        'exhibitions_list': exhibitions_list,
        'publications_list': publications_list,
        'page_title': 'About Jasem Shuman - Palestinian Contemporary Artist',
        'meta_description': 'Learn about Jasem Shuman, a contemporary Palestinian artist creating powerful paintings and sculptures.',
    }
    return render(request, 'pages/about.html', context)


def contact(request):
    """Contact page view with form submission"""
    if request.method == 'POST':
        # Handle AJAX form submission
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                # Debug: Log request details
                logger.info(f"Received AJAX request")
                logger.info(f"Content-Type: {request.content_type}")
                logger.info(f"Request body length: {len(request.body)}")
                
                # Parse JSON data
                try:
                    data = json.loads(request.body)
                    logger.info(f"Successfully parsed JSON data: {list(data.keys())}")
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    return JsonResponse({'success': False, 'errors': {'general': f'JSON decode error: {str(e)}'}})
                
                name = data.get('name', '').strip()
                email = data.get('email', '').strip()
                phone = data.get('phone', '').strip()
                contact_type = data.get('contact_type', 'general')
                subject = data.get('subject', '').strip()
                message = data.get('message', '').strip()
                
                logger.info(f"Form data: name={name}, email={email}, subject={subject}")
                
                # Validation
                errors = {}
                if not name:
                    errors['name'] = 'Name is required'
                if not email:
                    errors['email'] = 'Email is required'
                if not subject:
                    errors['subject'] = 'Subject is required'
                if not message:
                    errors['message'] = 'Message is required'
                
                if errors:
                    logger.info(f"Validation errors: {errors}")
                    return JsonResponse({'success': False, 'errors': errors})
                
                # Save contact submission
                try:
                    submission = ContactSubmission.objects.create(
                        name=name,
                        email=email,
                        phone=phone,
                        contact_type=contact_type,
                        subject=subject,
                        message=message
                    )
                    logger.info(f"Contact submission created successfully: {submission.id}")
                except Exception as e:
                    logger.error(f"Database error creating submission: {e}")
                    return JsonResponse({'success': False, 'errors': {'general': f'Database error: {str(e)}'}})
                
                # For now, let's skip email sending to isolate the issue
                logger.info("Skipping email sending for debugging")
                
                return JsonResponse({'success': True, 'message': 'Message sent successfully! (Debug mode - emails skipped)'})
                
            except Exception as e:
                error_message = f"Error: {type(e).__name__}: {str(e)}"
                logger.error(f"General error in contact form: {error_message}")
                return JsonResponse({'success': False, 'errors': {'general': error_message}})
        
        # Handle regular form submission (fallback)
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        contact_type = request.POST.get('contact_type', 'general')
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        
        # Basic validation
        if not all([name, email, subject, message]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'pages/contact.html', {
                'form_data': request.POST,
                'page_title': 'Contact - Jasem Shuman Art',
                'meta_description': 'Get in touch with Jasem Shuman for commissions, exhibitions, or general inquiries.',
            })
        
        # Save contact submission
        ContactSubmission.objects.create(
            name=name,
            email=email,
            phone=phone,
            contact_type=contact_type,
            subject=subject,
            message=message
        )
        
        messages.success(request, 'Thank you for your message! We will get back to you soon.')
        return render(request, 'pages/contact.html', {'success': True})
    
    # Get artwork ID if specified in query params (for artwork-specific inquiries)
    artwork_id = request.GET.get('artwork')
    
    context = {
        'artwork_id': artwork_id,
        'page_title': 'Contact - Jasem Shuman Art',
        'meta_description': 'Get in touch with Jasem Shuman for commissions, exhibitions, or general inquiries.',
    }
    return render(request, 'pages/contact.html', context)


def page_detail(request, slug):
    """Generic page detail view"""
    page = get_object_or_404(Page, slug=slug, is_published=True)
    
    context = {
        'page': page,
        'page_title': f'{page.title} - Jasem Shuman Art',
        'meta_description': page.meta_description or page.title,
    }
    return render(request, 'pages/page_detail.html', context)


def news_list(request):
    """News and updates listing"""
    news_updates = NewsUpdate.objects.filter(is_published=True).order_by('-publish_date')
    
    context = {
        'news_updates': news_updates,
        'page_title': 'News & Updates - Jasem Shuman Art',
        'meta_description': 'Latest news, exhibitions, and updates from Palestinian artist Jasem Shuman.',
    }
    return render(request, 'pages/news_list.html', context)


def news_detail(request, slug):
    """Individual news article view"""
    news_item = get_object_or_404(NewsUpdate, slug=slug, is_published=True)
    
    context = {
        'news_item': news_item,
        'page_title': f'{news_item.title} - Jasem Shuman Art',
        'meta_description': news_item.meta_description or news_item.summary,
    }
    return render(request, 'pages/news_detail.html', context)
