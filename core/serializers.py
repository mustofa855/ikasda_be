# core/serializers.py
from rest_framework import serializers
from .models import BPA, AuditLog, Direksi, DiscussionPost, DiscussionReply, EventRegistration, Gallery, GalleryAlbum, GalleryImage, Notification, StrategicDecision, User, AlumniProfile, News, Event, Donation, Feedback,Usage
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # Tambahkan field password
    # Tambahkan field verified agar bisa di-update
    verified = serializers.BooleanField(default=False)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'first_name', 'last_name', 'password', 'phone', 'verified','verification_requested'
]

    def create(self, validated_data):
        # Hapus password dari validated_data agar tidak disimpan secara plain text
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # Meng-hash password
        user.save()
        return user

class AlumniProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Nested representation

    class Meta:
        model = AlumniProfile
        fields = ['user', 'graduation_year', 'education', 'job', 'profile_photo']
        # Menambahkan 'profile_photo' agar foto profil juga ikut ditampilkan

class NewsSerializer(serializers.ModelSerializer):
    author_full_name = serializers.SerializerMethodField()
    author_profile_photo = serializers.SerializerMethodField()
    published_date_formatted = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = [
            'id', 'title', 'excerpt', 'content', 'image', 'category',
            'published_date', 'published_date_formatted',
            'author', 'author_full_name', 'author_profile_photo'
        ]

    def get_author_full_name(self, obj):
        if obj.author:
            first = obj.author.first_name or ""
            last = obj.author.last_name or ""
            return f"{first} {last}".strip() or obj.author.username
        return "Admin"

    def get_author_profile_photo(self, obj):
        if obj.author and hasattr(obj.author, 'profile') and obj.author.profile.profile_photo:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.author.profile.profile_photo.url)
        return ""

    def get_published_date_formatted(self, obj):
        import pytz
        jakarta_tz = pytz.timezone('Asia/Jakarta')
        local_time = obj.published_date.astimezone(jakarta_tz)
        return local_time.strftime("%d %b %Y, %H:%M WIB")


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = ['id', 'donor', 'name', 'email', 'amount', 'message', 'proof', 'created_at']
        read_only_fields = ['id', 'created_at', 'donor']

class FeedbackSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    profile_photo = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    verified = serializers.SerializerMethodField()

    class Meta:
        model = Feedback
        fields = ['id', 'full_name', 'profile_photo', 'message', 'created_at', 'likes_count', 'is_liked', 'verified']

    def get_full_name(self, obj):
        if obj.user:
            first = obj.user.first_name or ""
            last = obj.user.last_name or ""
            return f"{first} {last}".strip() or "Anonim"
        return "Anonim"

    def get_profile_photo(self, obj):
        request = self.context.get("request")
        if obj.user and hasattr(obj.user, 'profile') and obj.user.profile.profile_photo:
            return request.build_absolute_uri(obj.user.profile.profile_photo.url)
        return request.build_absolute_uri("/media/profile_photos/profile.png")

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return request.user in obj.likes.all()
        return False
    
    def get_verified(self, obj):
        return obj.user.verified  # Ambil status verifikasi dari model User



class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # Misalnya, jika model menyimpan role sebagai integer:
        data['user_role'] = self.user.role  
        # Jika model Anda menyimpan role sebagai string dan Anda ingin mengkonversinya ke integer,
        # Anda dapat melakukan misalnya:
        # role_map = {'alumni': 1, 'direksi': 2, 'bpa': 3}
        # data['user_role'] = role_map.get(self.user.role, 0)
        return data

class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = '__all__'

class UserWithProfileSerializer(serializers.ModelSerializer):
    profile = AlumniProfileSerializer(read_only=True)  # Nested representation dari AlumniProfile

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'first_name', 'last_name', 'phone', 'verified', 'profile', 'verification_requested']

class EventRegistrationSerializer(serializers.ModelSerializer):
    user_detail = UserWithProfileSerializer(source="user", read_only=True)
    class Meta:
        model = EventRegistration
        fields = ['id', 'event', 'user', 'user_detail', 'registration_date']
        read_only_fields = ('user', 'registration_date')

class DiscussionReplySerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    profile_photo = serializers.SerializerMethodField()
    verified = serializers.SerializerMethodField()

    class Meta:
        model = DiscussionReply
        fields = ['id', 'post', 'full_name', 'profile_photo', 'content', 'created_at', 'verified']

    def get_full_name(self, obj):
        if obj.user:
            first = obj.user.first_name or ""
            last = obj.user.last_name or ""
            return f"{first} {last}".strip() or "Anonim"
        return "Anonim"

    def get_profile_photo(self, obj):
        request = self.context.get("request")
        if obj.user and hasattr(obj.user, 'profile') and obj.user.profile.profile_photo:
            return request.build_absolute_uri(obj.user.profile.profile_photo.url)
        # Jika tidak ada foto, kembalikan default profile.png
        return request.build_absolute_uri("/media/profile_photos/profile.png")
    
    def get_verified(self, obj):
        return obj.user.verified


class DiscussionPostSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    profile_photo = serializers.SerializerMethodField()  # tambahkan field ini
    replies = DiscussionReplySerializer(many=True, read_only=True)
    verified = serializers.SerializerMethodField()

    class Meta:
        model = DiscussionPost
        fields = ['id', 'full_name', 'profile_photo', 'title', 'content', 'created_at', 'replies', 'verified']

    def get_full_name(self, obj):
        if obj.user:
            first = obj.user.first_name or ""
            last = obj.user.last_name or ""
            return f"{first} {last}".strip() or "Anonim"
        return "Anonim"

    def get_profile_photo(self, obj):
        # Asumsikan user memiliki hubungan one-to-one dengan AlumniProfile melalui atribut 'profile'
        if hasattr(obj.user, 'profile') and obj.user.profile.profile_photo:
            request = self.context.get("request")
            # Jika menggunakan request untuk membangun URL absolut
            return request.build_absolute_uri(obj.user.profile.profile_photo.url)
        return ""  # atau bisa dikembalikan URL default
    
    def get_verified(self, obj):
        return obj.user.verified

    
class AlumniProfileUpdateSerializer(serializers.ModelSerializer):
    # Gunakan source agar field ini bisa digunakan untuk GET dan update
    username = serializers.CharField(source='user.username', required=True)
    name = serializers.CharField(source='user.first_name', required=False)
    angkatan = serializers.IntegerField(source='graduation_year', required=False)
    pekerjaan = serializers.CharField(source='job', required=False)
    fotoProfil = serializers.ImageField(source='profile_photo', required=False)
    verified = serializers.BooleanField(source='user.verified', read_only=True)
    verification_requested = serializers.BooleanField(source='user.verification_requested', read_only=True)  # Tambahan field


    class Meta:
        model = AlumniProfile
        fields = ['username','name', 'angkatan', 'pekerjaan', 'fotoProfil', 'verified', 'verification_requested']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        if 'username' in user_data:
            instance.user.username = user_data.get('username')
        if 'first_name' in user_data:
            instance.user.first_name = user_data.get('first_name')
        instance.user.save()
        return super().update(instance, validated_data)
    

class UsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usage
        fields = ['id', 'description', 'amount', 'date']


class GalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryImage
        fields = '__all__'

class GalleryAlbumSerializer(serializers.ModelSerializer):
    images = GalleryImageSerializer(many=True, read_only=True)  # Foto-foto dalam album

    class Meta:
        model = GalleryAlbum
        fields = '__all__'

class StrategicDecisionSerializer(serializers.ModelSerializer):
    created_by = UserWithProfileSerializer(read_only=True)
    
    class Meta:
        model = StrategicDecision
        fields = ['id', 'title', 'description', 'decision_type', 'status', 'approval_reason', 'created_by', 'created_at']

# core/serializers.py

class AuditLogSerializer(serializers.ModelSerializer):
    user = UserWithProfileSerializer(read_only=True)
    
    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'action', 'details', 'timestamp']

class NotificationSerializer(serializers.ModelSerializer):
    user = UserWithProfileSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'user', 'title', 'message', 'link', 'is_read', 'created_at']

class DireksiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direksi
        fields = ['id', 'jabatan', 'nama']

class BPASerializer(serializers.ModelSerializer):
    class Meta:
        model = BPA
        fields = ['id', 'jabatan', 'nama']