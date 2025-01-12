"""
URL configuration for simplelms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from lms_core.views import index, testing, addData, editData, deleteData, register, user_dashboard, login_view, show_profile_teacher,show_profile_user, edit_profile, teacher_dashboard, batch_enroll_students, content_comments, moderate_comment, course_analytics, show_bookmarks, add_bookmark, delete_bookmark, available_courses_view, show_completion, add_completion, delete_completion, view_certificate, generate_certificate,delete_certificate, logout_view, user_content_comments
from lms_core.api import apiv1

urlpatterns = [
    path('api/v1/', apiv1.urls),
    path('admin/', admin.site.urls),
    path('testing/', testing),
    path('tambah/', addData),
    path('ubah/', editData),
    path('hapus/', deleteData),
    path('logout/', logout_view, name='logout'),
    path('register/', register, name='register'),  # Halaman register
    path('user/dashboard/', user_dashboard, name='user_dashboard'),
    path("profile_user/<int:user_id>/", show_profile_user, name="show_profile_user"),
    path("profile_teacher/<int:user_id>/", show_profile_teacher, name="show_profile_teacher"),
    path("profile/edit/", edit_profile, name="edit_profile"),
    path('teacher/dashboard/', teacher_dashboard, name='teacher_dashboard'),
    path("batch-enroll/", batch_enroll_students, name="batch_enroll_students"),
    path("contents/<int:content_id>/comments/", content_comments, name="content_comments"),
    path("comments/<int:comment_id>/moderate/", moderate_comment, name="moderate_comment"),
    path('content/<int:content_id>/comments/', user_content_comments, name='user_content_comments'),
    path("course/<int:course_id>/analytics/", course_analytics, name="course_analytics"),
    path('bookmarks/', show_bookmarks, name='show_bookmarks'), 
    path('bookmarks/add/', add_bookmark, name='add_bookmark'), 
    path('bookmarks/delete/<int:bookmark_id>/', delete_bookmark, name='delete_bookmark'),
    path("available-courses/", available_courses_view, name="available_courses"),
    path("completion/add/", add_completion, name="add_completion"),
    path("completion/", show_completion, name="show_completion"),
    path("completion/delete/<int:completion_id>/", delete_completion, name="delete_completion"),
    path("certificate/<int:certificate_id>/", view_certificate, name="view_certificate"),
    path("completion/generate/<int:course_id>/", generate_certificate, name="generate_certificate"),
    path("certificate/delete/<int:certificate_id>/", delete_certificate, name="delete_certificate"),
    path('', login_view, name="login"),
]
