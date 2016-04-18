import json
# Create your views here.
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, Http404, HttpResponseRedirect, redirect, get_object_or_404

from .models import Notification


@login_required
def all(request):
    notifications = Notification.objects.all_for_user(request.user)
    print("notifications", notifications)
    context = {"notifications": notifications,
               }
    return render(request, "notifications/all.html", context)


@login_required
def read(request, id):
    notification = get_object_or_404(Notification, id=id)
    try:
        # getting next value i.e. : /notifications/read/11/?next=/comment/92/
        next = request.GET.get('next', None)
        if notification.recipient == request.user:
            notification.read = True
            notification.save()
            if next is not None:
                return HttpResponseRedirect(next)
            else:
                return redirect("notifications_all")
        else:
            raise Http404
    except:
        return redirect("notifications_all")


@login_required
def get_notifications_ajax(request):
    notifications = Notification.objects.all_for_user(request.user).recent()
    print("notifications", notifications)
    if request.is_ajax() and request.method == "POST":
        notifications = Notification.objects.all_for_user(request.user).recent()
        print("notifications", notifications)
        count = notifications.count()
        notes = []
        for note in notifications:
            notes.append(str(note.get_link))

        data = {
                "notifications": notes,
                "count": count,
        }
        json_data = json.dumps(data)
        return HttpResponse(json_data, content_type='application/json')
    else:
        raise Http404
