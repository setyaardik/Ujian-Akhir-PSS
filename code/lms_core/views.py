from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.http import JsonResponse
from lms_core.models import Course, Comment, CourseContent, CourseMember, UserProfile, Bookmark, CompletionTracking, Certificate
from django.core import serializers
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def index(request):
    return HttpResponse("<h1>Hello World</h1>")
    
def testing(request):
    dataCourse = Course.objects.all()
    dataCourse = serializers.serialize("python", dataCourse)
    return JsonResponse(dataCourse, safe=False)

def addData(request):
    course = Course(
        name = "Belajar Django",
        description = "Belajar Django dengan Mudah",
        price = 1000000,
        teacher = User.objects.get(username="admin")
    )
    course.save()
    return JsonResponse({"message": "Data berhasil ditambahkan"})

def editData(request):
    course = Course.objects.filter(name="Belajar Django").first()
    course.name = "Belajar Django Setelah update"
    course.save()
    return JsonResponse({"message": "Data berhasil diubah"})

def deleteData(request):
    course = Course.objects.filter(name__icontains="Belajar Django").first()
    course.delete()
    return JsonResponse({"message": "Data berhasil dihapus"})

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already exists"})

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        return redirect('login')  # Ganti 'login' dengan nama URL untuk halaman login Anda

    return render(request, "register.html")

@login_required
def moderate_comment(request, comment_id):
    try:
        # Ambil komentar
        comment = get_object_or_404(Comment, id=comment_id)
        # Pastikan teacher hanya dapat memoderasi komentar pada konten kursus miliknya
        if comment.content_id.course_id.teacher != request.user:
            return JsonResponse({"error": "You are not allowed to moderate this comment"}, status=403)

        # Toggle status moderasi
        comment.is_approved = not comment.is_approved
        comment.save()

        return JsonResponse({
            "message": "Comment moderation status updated",
            "is_approved": comment.is_approved
        })
    except Comment.DoesNotExist:
        return JsonResponse({"error": "Comment not found"}, status=404)

@login_required
def user_dashboard(request):
    user = request.user
    stats = {
        "courses_joined": CourseMember.objects.filter(user_id=user, roles="std").count(),
        "courses_created": Course.objects.filter(teacher=user).count(),
        "comments_made": Comment.objects.filter(member_id__user_id=user).count(),
    }
    enrolled_courses = CourseMember.objects.filter(user_id=user, roles="std").select_related("course_id")
    enrolled_course_ids = enrolled_courses.values_list("course_id", flat=True)
    available_courses = Course.objects.exclude(id__in=enrolled_course_ids)
    return render(request, "user_dashboard.html", {"stats": stats, "enrolled_courses": enrolled_courses, "available_courses": available_courses})

@login_required
def show_profile(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        profile_data = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email
        }
        message = request.GET.get("message")
        return render(request, "show_profile.html", {"profile": profile_data, "user_id": user_id, "message": message})
    except User.DoesNotExist:
        return render(request, "show_profile.html")

@login_required
def edit_profile(request):
    if request.method == "POST":
        user = request.user
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.email = request.POST.get("email", user.email)
        user.save()
        return redirect(f"/profile/{user.id}/?message=Profile updated successfully")
    return render(request, "edit_profile.html", {"user": request.user})

@login_required
def batch_enroll_students(request):
    if request.method == "POST":
        course_id = request.POST.get("course_id")
        student_ids = request.POST.getlist("student_ids")  # Daftar ID siswa yang dipilih
        try:
            # Pastikan course dimiliki oleh teacher yang login
            course = get_object_or_404(Course, id=course_id, teacher=request.user)
            enrolled_students = []
            for student_id in student_ids:
                student = get_object_or_404(User, id=student_id)
                # Tambahkan student ke course jika belum menjadi member
                course_member, created = CourseMember.objects.get_or_create(
                    course_id=course, user_id=student, roles="std"
                )
                if created:
                    enrolled_students.append(student.username)
            return JsonResponse({"message": "Students enrolled successfully", "students": enrolled_students})
        except Course.DoesNotExist:
            return JsonResponse({"error": "Course not found or you do not have permission"}, status=403)
    courses = Course.objects.filter(teacher=request.user)
    students = User.objects.exclude(groups__name="Teachers")
    return render(request, "batch_enroll_students.html", {"courses": courses, "students": students})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        role = request.POST.get("role")  # Mendapatkan role dari form
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if role == "teacher" and user.groups.filter(name="Teachers").exists():
                login(request, user)
                return redirect("teacher_dashboard")
            elif role == "user" and not user.groups.filter(name="Teachers").exists():
                login(request, user)
                return redirect("user_dashboard")
            else:
                return render(request, "login.html", {"error": "Invalid role for the provided credentials"})
        return render(request, "login.html", {"error": "Invalid credentials"})
    return render(request, "login.html")


@login_required
def teacher_dashboard(request):
    courses = Course.objects.filter(teacher=request.user)
    course_count = courses.count()
    contents = CourseContent.objects.filter(course_id__in=courses)
    return render(request, "teacher_dashboard.html", {"courses": courses, "course_count": course_count, "contents": contents})

@login_required
def content_comments(request, content_id):
    content = get_object_or_404(CourseContent, id=content_id)
    comments = Comment.objects.filter(content_id=content, is_approved=True)  # Gunakan `content_id`
    return render(request, "content_comments.html", {"content": content, "comments": comments})

def course_analytics(request, course_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user)
    stats = {
        "total_members": CourseMember.objects.filter(course_id=course).count(),
        "total_contents": CourseContent.objects.filter(course_id=course).count(),
        "total_comments": Comment.objects.filter(content_id__course_id=course).count(),
    }
    return render(request, "course_analytics.html", {"course": course, "stats": stats})

def is_teacher(user):
    return user.groups.filter(name='Teachers').exists()

def is_user(user):
    return not user.groups.filter(name='Teachers').exists()

@login_required
def add_bookmark(request):
    if request.method == "POST":
        content_id = request.POST.get("content_id")
        try:
            content = CourseContent.objects.get(id=content_id)
            bookmark, created = Bookmark.objects.get_or_create(user=request.user, content=content)
            if created:
                return redirect(f"/bookmarks/?message=Bookmark added successfully")
            else:
                return redirect(f"/bookmarks/?message=Bookmark already exists")
        except CourseContent.DoesNotExist:
            return redirect(f"/bookmarks/?message=Content not found")
    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def show_bookmarks(request):
    bookmarks = Bookmark.objects.filter(user=request.user).select_related("content", "content__course_id")
    return render(request, "show_bookmarks.html", {"bookmarks": bookmarks})

@login_required
def delete_bookmark(request, bookmark_id):
    try:
        bookmark = Bookmark.objects.get(id=bookmark_id, user=request.user)
        bookmark.delete()
        return redirect(f"/bookmarks/?message=Bookmark deleted successfully")
    except Bookmark.DoesNotExist:
        return redirect(f"/bookmarks/?message=Bookmark not found")

@login_required
def available_courses_view(request):
    user = request.user
    enrolled_course_ids = CourseMember.objects.filter(user_id=user, roles="std").values_list("course_id", flat=True)
    available_courses = Course.objects.exclude(id__in=enrolled_course_ids)
    return render(request, "available_courses.html", {"available_courses": available_courses})

@login_required
def add_completion(request):
    if request.method == "POST":
        content_id = request.POST.get("content_id")
        try:
            content = CourseContent.objects.get(id=content_id)
            completion, created = CompletionTracking.objects.get_or_create(user=request.user, content=content)
            if created:
                messages.success(request, "Content marked as completed successfully.")
            else:
                messages.info(request, "Content is already marked as completed.")
        except CourseContent.DoesNotExist:
            messages.error(request, "Content not found.")
    return redirect(request.META.get('HTTP_REFERER', 'user_dashboard'))

from collections import defaultdict

@login_required
def show_completion(request):
    completions = CompletionTracking.objects.filter(user=request.user).select_related("content", "content__course_id")

    # Mengelompokkan konten yang selesai berdasarkan kursus
    courses_with_completion = defaultdict(list)
    for completion in completions:
        course = completion.content.course_id
        courses_with_completion[course].append(completion)

    # Cek kursus yang selesai seluruh kontennya
    completed_courses = []
    for course, completions in courses_with_completion.items():
        total_contents = CourseContent.objects.filter(course_id=course).count()
        if len(completions) == total_contents:  # Semua konten selesai
            certificate = Certificate.objects.filter(user=request.user, course=course).first()
            completed_courses.append({
                "course": course,
                "certificate": certificate,
            })

    return render(request, "show_completion.html", {
        "courses_with_completion": dict(courses_with_completion),
        "completed_courses": completed_courses,
    })



@login_required
def delete_completion(request, completion_id):
    try:
        # Menghapus completion berdasarkan ID dan user
        completion = CompletionTracking.objects.get(id=completion_id, user=request.user)
        completion.delete()
    except CompletionTracking.DoesNotExist:
        pass  # Abaikan jika data tidak ditemukan

    # Redirect kembali ke halaman sebelumnya (HTTP_REFERER)
    referer = request.META.get('HTTP_REFERER', 'show_completion')
    return redirect(referer)

@login_required
def view_certificate(request, certificate_id):
    certificate = get_object_or_404(Certificate, id=certificate_id, user=request.user)
    return render(request, "certificate.html", {"certificate": certificate})
    
@login_required
def generate_certificate(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    # Pastikan user telah menyelesaikan semua konten dalam kursus
    total_contents = CourseContent.objects.filter(course_id=course).count()
    completed_contents = CompletionTracking.objects.filter(user=request.user, content__course_id=course).count()

    if total_contents == completed_contents:
        # Buat sertifikat jika belum ada
        Certificate.objects.get_or_create(user=request.user, course=course)
        return redirect("show_completion")
    else:
        return JsonResponse({"error": "Course not fully completed"}, status=400)
    
def delete_certificate(request, certificate_id):
    try:
        # Mencari dan menghapus certificate berdasarkan ID dan user
        certificate = Certificate.objects.get(id=certificate_id, user=request.user)
        certificate.delete()
    except Certificate.DoesNotExist:
        pass  # Abaikan jika certificate tidak ditemukan

    # Redirect kembali ke halaman sebelumnya (HTTP_REFERER)
    referer = request.META.get('HTTP_REFERER', 'show_completion')
    return redirect(referer)

@login_required
def logout_view(request):
    logout(request)
    return redirect('login') 