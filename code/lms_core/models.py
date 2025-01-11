from django.db import models
from django.contrib.auth.models import User

# Tambahkan atribut baru untuk fitur Content Scheduling dan Moderation
class Course(models.Model):
    name = models.CharField("Nama Kursus", max_length=255)
    description = models.TextField("Deskripsi")
    price = models.IntegerField("Harga")
    image = models.ImageField("Gambar", upload_to="course", blank=True, null=True)
    teacher = models.ForeignKey(User, verbose_name="Pengajar", on_delete=models.RESTRICT)
    max_students = models.IntegerField("Maksimal Siswa", null=True, blank=True)
    created_at = models.DateTimeField("Dibuat pada", auto_now_add=True)
    updated_at = models.DateTimeField("Diperbarui pada", auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Mata Kuliah"
        verbose_name_plural = "Data Mata Kuliah"
        ordering = ["-created_at"]

    def is_member(self, user):
        return CourseMember.objects.filter(course_id=self, user_id=user).exists()

ROLE_OPTIONS = [('std', "Siswa"), ('ast', "Asisten")]

class CourseMember(models.Model):
    course_id = models.ForeignKey(Course, verbose_name="matkul", on_delete=models.RESTRICT)
    user_id = models.ForeignKey(User, verbose_name="siswa", on_delete=models.RESTRICT)
    roles = models.CharField("peran", max_length=3, choices=ROLE_OPTIONS, default='std')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Subscriber Matkul"
        verbose_name_plural = "Subscriber Matkul"

    def __str__(self) -> str:
        return f"{self.id} {self.course_id} : {self.user_id}"

class CourseContent(models.Model):
    name = models.CharField("judul konten", max_length=200)
    description = models.TextField("deskripsi", default='-')
    video_url = models.CharField('URL Video', max_length=200, null=True, blank=True)
    file_attachment = models.FileField("File", null=True, blank=True)
    course_id = models.ForeignKey(Course, verbose_name="matkul", on_delete=models.RESTRICT)
    parent_id = models.ForeignKey("self", verbose_name="induk", 
                                on_delete=models.RESTRICT, null=True, blank=True)
    release_date = models.DateTimeField("Tanggal Rilis", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Konten Matkul"
        verbose_name_plural = "Konten Matkul"

    def __str__(self) -> str:
        return f'{self.course_id} {self.name}'


class Comment(models.Model):
    content_id = models.ForeignKey(CourseContent, verbose_name="konten", on_delete=models.CASCADE)
    member_id = models.ForeignKey(CourseMember, verbose_name="pengguna", on_delete=models.CASCADE)
    comment = models.TextField('komentar')
    is_approved = models.BooleanField("Disetujui", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Komentar"
        verbose_name_plural = "Komentar"

    def __str__(self) -> str:
        return "Komen: "+self.member_id.user_id.username+"-"+self.comment

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField("First Name", max_length=30)
    last_name = models.CharField("Last Name", max_length=30)
    email = models.EmailField("Email")

    def __str__(self):
        return self.user.username
    
class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookmarks")
    content = models.ForeignKey(CourseContent, on_delete=models.CASCADE, related_name="bookmarked_by")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.content.name}"
<<<<<<< HEAD
    
class CompletionTracking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="completions")
    content = models.ForeignKey(CourseContent, on_delete=models.CASCADE, related_name="completed_by")
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "content")  # Ensures no duplicate completion
        verbose_name = "Completion Tracking"
        verbose_name_plural = "Completion Tracking"

    def __str__(self):
        return f"{self.user.username} completed {self.content.name}"
    
class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Certificate for {self.user.username} - {self.course.name}"
=======
>>>>>>> a6d12e6590c6164bff9e0c814824e42b97c0d8d4
