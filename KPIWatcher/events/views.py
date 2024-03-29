from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404, redirect
from django.shortcuts import render_to_response
from django.utils import timezone
from .forms import EventForm

from events.models import Event, Company


def all_events(request):
    events_all = Event.objects.all().order_by('-date_published')
    paginator = Paginator(events_all, 10)

    page = request.GET.get('page')

    if hasattr(request.user, 'teacher') or hasattr(request.user, 'company'):
        perm_to_create = True
    else:
        perm_to_create = False

    try:
        events = paginator.page(page)
    except PageNotAnInteger:
        events = paginator.page(1)
    except EmptyPage:
        events = paginator.page(paginator.num_pages)

    return render(request, 'events/all_events.html', {'events': events, 'perm_to_create': perm_to_create})


def event_page(request, pk):
    event = get_object_or_404(Event, pk=pk)
    subscribed = event.is_subscribed(request.user)
    return render(request, 'events/event_page.html', {'event': event, 'subscribed': subscribed})


def subscribe(request, pk):
    event = get_object_or_404(Event, pk=pk)
    event.subscribe(request.user)
    message = 'Thanks for subscribing!'
    return render(request, 'events/event_page.html', {'event': event, 'subscribed': True, 'message': message})


def unsubscribe(request, pk):
    event = get_object_or_404(Event, pk=pk)
    event.unsubscribe(request.user)
    return render(request, 'events/event_page.html', {'event': event, 'subscribed': False})


def create_new(request):
    if hasattr(request.user, 'teacher') or hasattr(request.user, 'company'):
        if request.method == "POST":
            form = EventForm(request.POST)
            if form.is_valid():
                event = form.save(commit=False)
                event.creator = request.user
                event.date_published = timezone.now()
                event.save()
                return redirect('events.views.event_page', pk=event.pk)
        else:
            form = EventForm()
        return render(request, 'events/edit_event_page.html', {'form': form})
    else:
        raise PermissionDenied()


def event_edit(request, pk):
    if hasattr(request.user, 'teacher') or hasattr(request.user, 'company'):
        event = get_object_or_404(Event, pk=pk)
        if request.method == "POST":
            form = EventForm(request.POST, instance=event)
            if form.is_valid():
                event = form.save(commit=False)
                event.creator = request.user
                event.date_published = timezone.now()
                event.save()
                return redirect('events.views.event_page', pk=event.pk)
        else:
            form = EventForm(instance=event)
        return render(request, 'events/edit_event_page.html', {'form': form})
    else:
        raise PermissionDenied()


def company_page(request, pk):
    company = get_object_or_404(Company, pk=pk)
    return render_to_response('events/company_page.html', {'company': company})


def all_companies(request):
    companies_all = Company.objects.all()
    paginator = Paginator(companies_all, 20)

    page = request.GET.get('page')

    try:
        companies = paginator.page(page)
    except PageNotAnInteger:
        companies = paginator.page(1)
    except EmptyPage:
        companies = paginator.page(paginator.num_pages)

    return render(request, 'events/all_companies.html', {'companies': companies})
