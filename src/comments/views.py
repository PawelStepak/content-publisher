from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, Http404, HttpResponseRedirect, get_object_or_404
from rest_framework import generics, mixins, permissions
# Create your views here.
from notifications.signals import notify
from videos.models import Video
from .models import Comment
from .forms import CommentForm

from .permissions import IsOwnerOrReadOnly
from .serializers import CommentCreateSerializer, CommentUpdateSerializer, CommentSerializer


class CommentListAPIView(generics.ListAPIView):
    # authentication_classes = [SessionAuthentication,
    # BasicAuthentication,
    # JSONWebTokenAuthentication]
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    paginate_by = 10


class CommentAPICreateView(generics.CreateAPIView):
    serializer_class = CommentCreateSerializer


class CommentDetailAPIView(mixins.DestroyModelMixin,
                           mixins.UpdateModelMixin,
                           generics.RetrieveAPIView):

    queryset = Comment.objects.all()
    serializer_class = CommentUpdateSerializer
    permission_classes = [IsOwnerOrReadOnly, ]
    lookup_field = 'id'

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


@login_required
def comment_thread(request, id):
    comment = get_object_or_404(Comment, id=id)
    form = CommentForm()
    context = {"form": form,
               "comment": comment
               }
    return render(request, "comments/comment_thread.html", context)


def comment_create_view(request):
    if request.method == "POST" and request.user.is_authenticated():

        parent_id = request.POST.get('parent_id')
        video_id = request.POST.get("video_id")

        # origin_path variable is used only for new comment that doesn't have parent
        origin_path = request.POST.get("origin_path")
        ###

        try:
            video = Video.objects.get(id=video_id)
        except:
            video = None

        parent_comment = None

        if parent_id is not None:
            try:
                parent_comment = Comment.objects.get(id=parent_id)
            except:
                parent_comment = None

            if parent_comment is not None and parent_comment.video is not None:
                video = parent_comment.video

        form = CommentForm(request.POST)
        if form.is_valid():
            comment_text = form.cleaned_data['comment']

            if parent_comment is not None:
                new_comment = Comment.objects.create_comment(user=request.user,
                                                             # path=request.get_full_path(),
                                                             path=parent_comment.get_origin,
                                                             #
                                                             text=comment_text,
                                                             video=video,
                                                             parent=parent_comment
                                                             )
                messages.success(request,
                                 "Thank you for your response",
                                 extra_tags='alert-warning')
                notify.send(
                            request.user,
                            action=new_comment,
                            target=parent_comment,
                            recipient=parent_comment.user,
                            affected_users=parent_comment.get_affected_users(),
                            verb='replied to'
                            )
                # print "parent_comment.get_absolute_url()", parent_comment.get_absolute_url()
                return HttpResponseRedirect(parent_comment.get_absolute_url())
            else:
                new_comment = Comment.objects.create_comment(user=request.user,
                                                             #
                                                             # path=request.get_full_path(),
                                                             path=origin_path,
                                                             #
                                                             text=comment_text,
                                                             video=video,
                                                             )
                # option to send to super user or staff users
#                 notify.send(
#                             request.user,
#                             action=new_comment,
#                             target=new_comment.video,
#                             recipient=request.user,
#                             verb='commented on'
#                             )
                messages.success(request, "Thank you for the comment.")
                # notify.send(request.user, recipient=request.user, action='new comment')
                # print "new_comment.get_absolute_url()", new_comment.get_absolute_url()
                return HttpResponseRedirect(new_comment.get_absolute_url())
        else:
            messages.error(request, "There was an error with your comment.")
            return HttpResponseRedirect(origin_path)

    else:
        raise Http404
