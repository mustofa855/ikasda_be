import os
import random
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser

class RandomFilename:
    """
    Callable class untuk menghasilkan nama file acak di folder yang ditentukan.
    Metode deconstruct() diperlukan agar objek ini dapat diserialisasi oleh Django.
    """
    def __init__(self, folder):
        self.folder = folder

    def __call__(self, instance, filename):
        # Dapatkan ekstensi file (misalnya: .jpg, .png)
        ext = os.path.splitext(filename)[1]
        # Hasilkan angka acak antara 1000000000 dan 9999999999
        random_number = random.randint(1000000000, 9999999999)
        # Buat nama file baru
        new_filename = f"{random_number}{ext}"
        # Kembalikan path upload, misalnya "folder/nama_file"
        return os.path.join(self.folder, new_filename)

    def deconstruct(self):
        """
        Mengembalikan tuple (import_path, args, kwargs) agar dapat diserialisasi oleh Django.
        """
        return (
            "core.models.RandomFilename",  # Import path lengkap ke kelas ini
            [self.folder],                 # Argumen posisi
            {}                             # Argumen keyword (kosong)
        )

# Custom User dengan Role
class User(AbstractUser):
    ROLE_CHOICES = (
        ('alumni', 'Alumni'),
        ('admin', 'Admin'),
        ('direksi', 'Direksi'),
        ('bpa', 'BPA'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='alumni')
    phone = models.CharField(max_length=15)
    email = models.CharField(max_length=255)
    verified = models.BooleanField(default=False)  # Field verifikasi alumni
    verification_requested = models.BooleanField(default=False)
    # Field tambahan lainnya sesuai kebutuhan

# Profil Alumni (jika ingin dipisah dari User)
class AlumniProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    graduation_year = models.IntegerField()  # angkatan
    education = models.CharField(max_length=255)
    job = models.CharField(max_length=255, blank=True, null=True)
    # Gunakan RandomFilename untuk upload_to pada foto profil
    profile_photo = models.ImageField(
        upload_to=RandomFilename('profile_photos'),
        blank=True,
        null=True,
        default='profile_photos/profile.png'
    )

    def __str__(self):
        return f"{self.user.username} - {self.graduation_year}"

# Model Berita/Blog
class News(models.Model):
    CATEGORY_CHOICES = (
        ('Sport', 'Sport'),
        ('Sosial', 'Kegiatan Sosial'),
        ('Pendidikan', 'Pendidikan'),
        ('Hiburan', 'Hiburan'),
        ('Politik', 'Politik'),
        ('Ekonomi', 'Ekonomi'),
        ('Teknologi', 'Teknologi'),
        ('Kesehatan', 'Kesehatan'),
        ('Budaya', 'Budaya'),
        ('Otomotif', 'Otomotif'),
        ('Pengumuman', 'Pengumuman'),
    )
    title = models.CharField(max_length=255)
    excerpt = models.TextField(blank=True, null=True)
    content = models.TextField()
    # Simpan gambar berita dengan nama acak di folder 'news_images'
    image = models.ImageField(
        upload_to=RandomFilename('news_images'),
        blank=True,
        null=True
    )
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, blank=True, null=True)
    published_date = models.DateTimeField(auto_now_add=True)
    # Field author untuk menyimpan pembuat berita (boleh null jika tidak di-set)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='news_posts'
    )
    
    def __str__(self):
        return self.title

# Model Event
class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True, null=True)
    # Simpan gambar event dengan nama acak di folder 'event_images'
    image = models.ImageField(
        upload_to=RandomFilename('event_images'),
        blank=True,
        null=True
    )
    # Field tambahan: misalnya kuota peserta, dll.

    def __str__(self):
        return self.title

# Model Donasi
class Donation(models.Model):
    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='donations',
        blank=True,
        null=True
    )
    name = models.CharField(max_length=200)
    email = models.EmailField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True, null=True)
    # Simpan bukti donasi dengan nama acak di folder 'donation_proofs'
    proof = models.FileField(
        upload_to=RandomFilename('donation_proofs'),
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Donasi oleh {self.name} - {self.amount}"

# Model Kesan & Pesan / Feedback
class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # Field untuk menyimpan user yang memberi like
    likes = models.ManyToManyField(User, related_name='liked_feedbacks', blank=True)

    def __str__(self):
        return f"Feedback dari {self.user.username}"

# Model Pendaftaran Event
class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    registration_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')  # Mencegah pendaftaran ganda

    def __str__(self):
        return f"{self.user.username} registered for {self.event.title}"

# Model Gallery
class Gallery(models.Model):
    title = models.CharField(max_length=255)
    # Simpan gambar galeri dengan nama acak di folder 'gallery_images'
    image = models.ImageField(
        upload_to=RandomFilename('gallery_images')
    )
    description = models.TextField(blank=True, null=True)
    uploaded_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# Model Album Gallery
class GalleryAlbum(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    # Simpan cover album dengan nama acak di folder 'gallery_albums'
    cover_image = models.ImageField(
        upload_to=RandomFilename('gallery_albums'),
        blank=True,
        null=True
    )
    uploaded_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# Model Gambar di dalam Album Gallery
class GalleryImage(models.Model):
    album = models.ForeignKey(GalleryAlbum, on_delete=models.CASCADE, related_name="images")
    # Simpan gambar dalam album dengan nama acak di folder 'gallery_images'
    image = models.ImageField(
        upload_to=RandomFilename('gallery_images')
    )
    caption = models.CharField(max_length=255, blank=True, null=True)
    uploaded_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image in {self.album.title}"

# Model Diskusi / Post
class DiscussionPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="discussion_posts")
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# Model Balasan Diskusi
class DiscussionReply(models.Model):
    post = models.ForeignKey(DiscussionPost, on_delete=models.CASCADE, related_name="replies")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="discussion_replies")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply by {self.user.username} on {self.post.title}"

# Model Penggunaan (Usage)
class Usage(models.Model):
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # Menggunakan auto_now_add agar tanggal di-set saat pembuatan record
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} - {self.amount}"

# Model Keputusan Strategis
class StrategicDecision(models.Model):
    DECISION_TYPE_CHOICES = (
        ('event', 'Event Besar'),
        ('policy', 'Kebijakan'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    decision_type = models.CharField(max_length=50, choices=DECISION_TYPE_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='strategic_decisions')
    approval_reason = models.TextField(blank=True, null=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_strategic_decisions'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.decision_type} ({self.status})"

# Model Audit Log
class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    details = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.timestamp} - {self.user}: {self.action}"

# Model Notifikasi
class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.URLField(blank=True, null=True)  # Opsional, jika ingin memberikan tautan ke detail
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.user.username if self.user else 'No User'}"
