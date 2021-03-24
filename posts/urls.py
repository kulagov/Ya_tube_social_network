from django.urls import path

from . import views

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    # path('follow/', views.Index.as_view(), name='follow_index'),
    path('follow/', views.FollowIndex.as_view(), name='follow_index'),
    path('group/<slug:slug>/', views.GroupPosts.as_view(), name='group'),
    path('new/', views.NewPost.as_view(), name='new_post'),
    path('<str:username>/', views.Profile.as_view(), name='profile'),
    # path('<str:username>/<int:pk>/', views.PostView.as_view(), name='post'),
    path('<str:username>/<int:pk>/', views.post_view, name='post'),
    path(
        '<str:username>/<int:pk>/edit/',
        views.PostEdit.as_view(),
        name='post_edit'
    ),
    path(
        '<str:username>/<int:pk>/comment',
        views.add_comment,
        name='add_comment'
    ),
    path(
        '<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),
    path(
        '<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    )
]
