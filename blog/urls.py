from django.urls import path
from .views import BlogPostListCreateView, BlogPostDetailView, CommentListCreateView, CommentDetailView, BlogPostFilterView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Blog post endpoints
    path('posts/', BlogPostListCreateView.as_view(), name='post-list'),
    path('posts/<int:pk>/', BlogPostDetailView.as_view(), name='post-detail'),

    # Comment endpoints
    path('posts/<int:post_id>/comments/', CommentListCreateView.as_view(), name='comment-list'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),

    # Filter endpoints
    path('posts/filter/', BlogPostFilterView.as_view(), name='post-filter'),

]