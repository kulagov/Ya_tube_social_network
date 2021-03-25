from django.contrib.auth.decorators import login_required
from django.shortcuts import (get_list_or_404, get_object_or_404, redirect,
                              render)
from django.urls import reverse_lazy
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, ListView, UpdateView

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User


class Index(ListView):
    template_name = 'posts/index.html'
    paginate_by = 10
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = context.pop('page_obj')
        return context


@method_decorator(login_required, name='dispatch')
class FollowIndex(Index):
    template_name = 'posts/follow.html'

    def get_queryset(self):
        self.following = Follow.objects.filter(
            user=self.request.user
        ).values('author')
        print(self.following)
        test1 = self.request.user.follower.all()
        print(test1)
        return Post.objects.filter(author__in=self.following)

@login_required
def profile_follow(request, username):
    user = request.user
    author = User.objects.get(username=username)
    if not Follow.objects.filter(user=user, author=author).exists():
        Follow.objects.create(user=user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = User.objects.get(username=username)
    link_follow = get_object_or_404(Follow, user=user, author=author)
    link_follow.delete()
    return redirect('profile', username=username)


class GroupPosts(ListView):
    template_name = 'group.html'
    paginate_by = 10
    context_object_name = 'posts'

    def get_queryset(self):
        self.group = get_object_or_404(Group, slug=self.kwargs['slug'])
        return self.group.posts.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.group
        context['page'] = context.pop('page_obj')
        return context


class Profile(ListView):
    template_name = 'posts/profile.html'
    paginate_by = 10

    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        return self.author.posts.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = context.pop('page_obj')
        context['author'] = self.author
        # context['author_card'] = {
        #     'records': self.author.posts.count(),
        #     # 'subscribers': 'FIXME',  # FIXME
        #     # 'subscribed': 'FIXME',  # FIXME
        # }
        # # print(Follow.objects.)
        user = self.request.user
        author = self.author
        context['following'] = Follow.objects.filter(
            user=user, author=author
        ).exists()
        return context

# переписать
# class PostView(DetailView):
#     template_name = 'posts/post.html'
#     form_class = CommentForm
#     model = Comment

#     def get_queryset(self):
#         self.author = get_object_or_404(User, username=self.kwargs['username'])
#         self.post = get_object_or_404(Post, id=self.kwargs['pk'])
#         return Post.objects.filter(id=self.kwargs['pk'], author=self.author)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['author'] = 'fixme'  #  self.author
#         context['author_card'] = {
#             'records': 0,  # self.author.posts.count(),
#             'subscribers': 'FIXME',  # FIXME
#             'subscribed': 'FIXME',  # FIXME
#         }
#         return context

@method_decorator(login_required, name='dispatch')
class PostEdit(UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'posts/newpost.html'

    def get_success_url(self):
        return reverse('post', args=self.args, kwargs=self.kwargs)

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            return redirect('post', *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class NewPost(CreateView):
    model = Post
    fields = ['group', 'text', 'image']
    template_name = 'posts/newpost.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        return super().form_valid(form)


def post_view(request, username, pk):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=pk)
    comments = Comment.objects.filter(post=post).all()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            # print(new_comment)
            new_comment.save()
    form = CommentForm()
    content = {
        'post': post,
        'author': author,
        'author_card': {
            'records': author.posts.count(),
            'subscribers': 'FIXME',  # FIXME
            'subscribed': 'FIXME',  # FIXME
        },
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post.html', content)

add_comment = post_view

def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)
