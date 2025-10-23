from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from .models import Page, NewsUpdate, ContactSubmission


def about(request):
    """About page view"""
    try:
        about_page = Page.objects.get(page_type='about', is_published=True)
    except Page.DoesNotExist:
        about_page = None
    
    context = {
        'page': about_page,
        'page_title': 'About Jasem Shuman - Palestinian Contemporary Artist',
        'meta_description': 'Learn about Jasem Shuman, a contemporary Palestinian artist creating powerful paintings and sculptures.',
    }
    return render(request, 'pages/about.html', context)


def contact(request):
    """Contact page view with form submission"""
    if request.method == 'POST':
        # Handle contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        contact_type = request.POST.get('contact_type', 'general')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Save contact submission
        ContactSubmission.objects.create(
            name=name,
            email=email,
            phone=phone,
            contact_type=contact_type,
            subject=subject,
            message=message,
            user=request.user if request.user.is_authenticated else None
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
