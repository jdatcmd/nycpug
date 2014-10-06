from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.views.decorators.cache import never_cache

from nycpug.app.account.forms import *

from .forms import ProposalForm
from .models import Article, Conference, Event, Room

def home(request):
    """the homepage - which redirects to the current Conference context"""
    conference =  get_object_or_404(Conference, active=True)
    return redirect(reverse('conference' , args=[conference.slug]))

def conference(request, slug):
    """the actual conference homepage"""
    articles = Article.objects.filter(published=True).order_by('-created_at').all()
    return render_to_response('home.html', {
        'articles': articles,
    }, RequestContext(request))

def schedule(request, slug):
    """list the schedule...one day"""
    return render_to_response('schedule.html', {}, RequestContext(request))

def speaker(request, slug, event_id):
    """render information for a speaker"""
    event = get_object_or_404(Event, id=event_id)
    return render_to_response('speaker.html', { 'event': event }, RequestContext(request))

@never_cache # causes issues with reloading data from form
def submit(request, slug, proposal_id=None):
    """
    here the user can:
    a) register for an account, if the user has not already done so OR
    b) view talk submissions that user has submitted AND submit new talks

    """
    print request.user.is_authenticated()
    if not request.user.is_authenticated():
        request.session['next'] = request.path
        return render_to_response('submit.html', {
            'conference': request.conference,
            'login_form': LoginForm(),
            'signup_form': SignupForm(),
        }, RequestContext(request))
    else:
        if proposal_id:
            proposal = get_object_or_404(request.user.proposals, conference=request.conference, id=proposal_id)
        else:
            proposal = None
        proposals = request.conference.proposals.filter(user=request.user)
        if request.method == 'POST':
            form = ProposalForm(request.POST, request=request, instance=proposal)
            if form.is_valid():
                form.save()
                return redirect(reverse('submit', args=[request.conference.slug]))
        else:
            form = ProposalForm(request=request, instance=proposal)
        return render_to_response('submit.html', {
            'conference': request.conference,
            'form': form,
            'proposal': proposal,
            'proposals': proposals,
        }, RequestContext(request))
