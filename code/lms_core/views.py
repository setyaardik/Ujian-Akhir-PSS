from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.http import JsonResponse
from lms_core.models import Course, Comment, CourseContent, CourseMember, UserProfile
from django.core import serializers
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login

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
        # Login pengguna setelah registrasi
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"message": "User registered and logged in successfully"})

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
    return render(request, "user_dashboard.html", {"stats": stats})

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
