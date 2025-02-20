# Create your views here.
# core/views.py
from django.utils import timezone
from rest_framework import viewsets, permissions, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from django.db.models import Count, Sum
from rest_framework.permissions import IsAuthenticated, BasePermission


from core.permissions import IsDireksi, IsDireksiOrReadOnly
from .models import BPA, AlumniProfile, AuditLog, Direksi, DiscussionPost, DiscussionReply, EventRegistration, Gallery, GalleryAlbum, GalleryImage, News, Event, Donation, Feedback, StrategicDecision, Usage, User
from .serializers import AlumniProfileSerializer, AlumniProfileUpdateSerializer, AuditLogSerializer, BPASerializer, DireksiSerializer, DiscussionPostSerializer, DiscussionReplySerializer, EventRegistrationSerializer, GalleryAlbumSerializer, GalleryImageSerializer, GallerySerializer, NewsSerializer, EventSerializer, DonationSerializer, FeedbackSerializer, NotificationSerializer, StrategicDecisionSerializer, UsageSerializer, UserSerializer, UserWithProfileSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer

# Endpoint untuk Berita (publik)
class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all().order_by('-published_date')
    serializer_class = NewsSerializer
    permission_classes = [IsDireksiOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

# Endpoint untuk Event
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('start_date')
    serializer_class = EventSerializer
    permission_classes = [IsDireksiOrReadOnly]
    # Untuk admin, kamu bisa override metode seperti perform_create()

# Endpoint untuk Donasi (hanya alumni yang telah login)
class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all().order_by('-created_at')
    serializer_class = DonationSerializer
    permission_classes = [permissions.AllowAny]  # Siapa saja dapat melihat dan mengirim donasi

    def perform_create(self, serializer):
        # Jika user sudah login, set donor; jika tidak, simpan tanpa donor
        if self.request.user and self.request.user.is_authenticated:
            serializer.save(donor=self.request.user)
        else:
            serializer.save()

# Endpoint untuk Feedback/Kesan & Pesan
class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all().order_by('-created_at')
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        feedback = self.get_object()
        user = request.user
        if user in feedback.likes.all():
            feedback.likes.remove(user)
            liked = False
        else:
            feedback.likes.add(user)
            liked = True
        return Response({
            'liked': liked,
            'likes_count': feedback.likes.count()
        })

# Endpoint Registrasi Alumni
# core/views.py

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Pastikan user langsung aktif (meskipun defaultnya sudah True)
            user.is_active = True
            user.save()
            # Jika role user adalah alumni, bpa, atau direksi, buat AlumniProfile
            if user.role in ['alumni', 'bpa', 'direksi']:
                AlumniProfile.objects.create(
                    user=user,
                    graduation_year=request.data.get('graduation_year'),
                    education=request.data.get('education'),
                    job=request.data.get('job')
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class EventRegistrationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Hanya alumni yang dapat mendaftar event
        if request.user.role != 'alumni':
            return Response(
                {"detail": "Hanya alumni yang dapat mendaftar event."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Pastikan data yang dikirim mencakup field 'event'
        event_id = request.data.get("event")
        if not event_id:
            return Response(
                {"detail": "Event ID diperlukan."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Untuk mencegah pendaftaran ganda, periksa apakah user sudah mendaftar event tersebut
        if EventRegistration.objects.filter(event_id=event_id, user=request.user).exists():
            return Response(
                {"detail": "Anda sudah mendaftar untuk event ini."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = EventRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            # Set user yang mendaftar secara otomatis
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_queryset(self):
        queryset = EventRegistration.objects.all().order_by('-registration_date')
        event_id = self.request.query_params.get("event", None)
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        return queryset

    
class EventRegistrationListView(generics.ListAPIView):
    """
    API endpoint untuk direksi melihat daftar pendaftaran event.
    Hanya user dengan peran 'direksi' yang diizinkan.
    """
    serializer_class = EventRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated, IsDireksi]

    def get_queryset(self):
        # Mengembalikan semua pendaftaran event, bisa diurutkan berdasarkan tanggal pendaftaran terbaru.
        return EventRegistration.objects.all().order_by('-registration_date')

class GalleryViewSet(viewsets.ModelViewSet):
    queryset = Gallery.objects.all().order_by('-uploaded_date')
    serializer_class = GallerySerializer
    # Hanya direksi yang bisa membuat, mengubah, atau menghapus gambar di gallery.
    permission_classes = [IsDireksiOrReadOnly]


class AlumniProfileViewSet(viewsets.ModelViewSet):
    queryset = AlumniProfile.objects.all().order_by('user__username')
    serializer_class = AlumniProfileSerializer
    permission_classes = [permissions.IsAuthenticated]  # Atur sesuai kebutuhan; hanya direksi yang boleh mengakses

# ---------------------------
# UserViewSet dengan fitur reset password
# ---------------------------
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('username')
    serializer_class = UserWithProfileSerializer
    permission_classes = [permissions.IsAuthenticated]  # Sesuaikan permission sesuai kebutuhan

    @action(detail=True, methods=['post'], url_path='reset-password', permission_classes=[permissions.IsAuthenticated])
    def reset_password(self, request, pk=None):
        # Hanya admin (atau direksi) yang boleh reset password
        if request.user.role != 'direksi':
            return Response({'detail': 'Hanya admin yang dapat mereset password.'}, status=status.HTTP_403_FORBIDDEN)
        
        user = self.get_object()
        new_password = request.data.get('new_password')
        if not new_password:
            return Response({'detail': 'Password baru harus diberikan.'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Password berhasil direset.'}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """
        Override update untuk menangani pembaruan data user dan data profile secara nested.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data
        # Update field user
        instance.username = data.get('username', instance.username)
        instance.first_name = data.get('first_name', instance.first_name)
        instance.last_name = data.get('last_name', instance.last_name)
        instance.email = data.get('email', instance.email)
        instance.phone = data.get('phone', instance.phone)
        instance.role = data.get('role', instance.role)
        # Tambahkan update untuk field verified jika dikirim
        if 'verified' in data:
            instance.verified = data.get('verified')
        instance.save()

        # Update field profile jika ada data nested
        profile_data = data.get('profile', None)
        if profile_data:
            profile = instance.profile
            profile.graduation_year = profile_data.get('graduation_year', profile.graduation_year)
            profile.education = profile_data.get('education', profile.education)
            profile.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

# ---------------------------
# View untuk Pengelompokan Alumni
# ---------------------------
class AlumniGroupingView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Hanya admin yang dapat mengakses

    def get(self, request):
        group_by = request.query_params.get("group_by", "graduation_year")
        if group_by == "graduation_year":
            groups = AlumniProfile.objects.values("graduation_year").annotate(total=Count("id")).order_by("graduation_year")
            data = []
            for group in groups:
                alumni = AlumniProfile.objects.filter(graduation_year=group["graduation_year"])
                serializer = AlumniProfileSerializer(alumni, many=True, context={"request": request})
                data.append({
                    "graduation_year": group["graduation_year"],
                    "total": group["total"],
                    "alumni": serializer.data
                })
            return Response(data, status=status.HTTP_200_OK)
        elif group_by == "education":
            groups = AlumniProfile.objects.values("education").annotate(total=Count("id")).order_by("education")
            data = []
            for group in groups:
                alumni = AlumniProfile.objects.filter(education=group["education"])
                serializer = AlumniProfileSerializer(alumni, many=True, context={"request": request})
                data.append({
                    "education": group["education"],
                    "total": group["total"],
                    "alumni": serializer.data
                })
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Parameter group_by tidak valid.'}, status=status.HTTP_400_BAD_REQUEST)

class DiscussionPostViewSet(viewsets.ModelViewSet):
    queryset = DiscussionPost.objects.all().order_by('-created_at')
    serializer_class = DiscussionPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DiscussionReplyViewSet(viewsets.ModelViewSet):
    queryset = DiscussionReply.objects.all().order_by('created_at')
    serializer_class = DiscussionReplySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AlumniProfileUpdateView(generics.RetrieveUpdateAPIView):
    """
    Endpoint bagi user dengan role alumni untuk mengambil (GET) dan memperbarui (PATCH)
    data profilnya sendiri.
    """
    serializer_class = AlumniProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Dapatkan AlumniProfile user, buat baru jika belum ada.
        profile, created = AlumniProfile.objects.get_or_create(
            user=self.request.user,
            defaults={
                'graduation_year': 0,  # default value jika belum ada
                'education': '',
                'job': '',
            }
        )
        return profile
    

class UsageViewSet(viewsets.ModelViewSet):
    queryset = Usage.objects.all().order_by('-date')
    serializer_class = UsageSerializer
    permission_classes = [permissions.IsAuthenticated]

class GalleryAlbumViewSet(viewsets.ModelViewSet):
    queryset = GalleryAlbum.objects.all().order_by('-uploaded_date')
    serializer_class = GalleryAlbumSerializer
    permission_classes = [IsDireksiOrReadOnly]  # Sesuaikan permission sesuai kebutuhan

class GalleryImageViewSet(viewsets.ModelViewSet):
    queryset = GalleryImage.objects.all().order_by('-uploaded_date')
    serializer_class = GalleryImageSerializer
    permission_classes = [IsDireksiOrReadOnly]

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_verification(request):
    user = request.user
    # Cek jika user sudah terverifikasi
    if user.verified:
        return Response({"detail": "Akun sudah terverifikasi."}, status=status.HTTP_400_BAD_REQUEST)
    # Tandai bahwa user telah mengajukan verifikasi
    user.verification_requested = True
    user.save()
    return Response({"detail": "Permintaan verifikasi telah dikirim."}, status=status.HTTP_200_OK)


class MyEventRegistrationListView(generics.ListAPIView):
    serializer_class = EventRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Kembalikan pendaftaran event milik user yang sedang login
        return EventRegistration.objects.filter(user=self.request.user).order_by('-registration_date')

from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import StrategicDecision
from .serializers import StrategicDecisionSerializer

class IsDireksi(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'direksi'

class IsBPA(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'bpa'

class IsDireksiOrBPA(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['direksi', 'bpa']

from .models import StrategicDecision, AuditLog  # Pastikan AuditLog diimport

class StrategicDecisionViewSet(viewsets.ModelViewSet):
    queryset = StrategicDecision.objects.all()
    serializer_class = StrategicDecisionSerializer

    def get_permissions(self):
        if self.action in ['approve', 'reject']:
            permission_classes = [IsAuthenticated, IsBPA]
        elif self.request.method == "GET":
            permission_classes = [IsAuthenticated, IsDireksiOrBPA]
        else:
            permission_classes = [IsAuthenticated, IsDireksi]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        decision = self.get_object()
        if decision.status != 'pending':
            return Response({'detail': 'Keputusan sudah diproses.'}, status=400)
        decision.status = 'approved'
        decision.approved_by = request.user
        decision.approved_at = timezone.now()
        decision.approval_reason = request.data.get('approval_reason', '')
        decision.save()

        # Tambahkan pembuatan log audit
        AuditLog.objects.create(
            user=request.user,
            action="Approve Strategic Decision",
            details=f"Keputusan '{decision.title}' disetujui. Alasan: {decision.approval_reason}"
        )
        return Response({'detail': 'Keputusan disetujui.'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        decision = self.get_object()
        if decision.status != 'pending':
            return Response({'detail': 'Keputusan sudah diproses.'}, status=400)
        decision.status = 'rejected'
        decision.approved_by = request.user
        decision.approved_at = timezone.now()
        decision.approval_reason = request.data.get('approval_reason', '')
        decision.save()

        # Tambahkan pembuatan log audit
        AuditLog.objects.create(
            user=request.user,
            action="Reject Strategic Decision",
            details=f"Keputusan '{decision.title}' ditolak. Alasan: {decision.approval_reason}"
        )
        return Response({'detail': 'Keputusan ditolak.'})



# Endpoint dashboard direksi untuk menampilkan ringkasan laporan
class DireksiDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsDireksi]

    def get(self, request):
        total_donations = Donation.objects.aggregate(total=Sum('amount'))['total'] or 0
        donation_count = Donation.objects.count()
        total_events = Event.objects.count()
        upcoming_events = Event.objects.filter(start_date__gte=timezone.now()).order_by('start_date')[:5]
        event_registrations_count = EventRegistration.objects.count()
        strategic_decisions_count = StrategicDecision.objects.count()

        upcoming_events_data = [
            {
                "id": event.id,
                "title": event.title,
                "start_date": event.start_date,
                "end_date": event.end_date,
                "location": event.location,
            } for event in upcoming_events
        ]
        data = {
            "total_donations_amount": total_donations,
            "donation_count": donation_count,
            "total_events": total_events,
            "upcoming_events": upcoming_events_data,
            "event_registrations_count": event_registrations_count,
            "strategic_decisions_count": strategic_decisions_count,
        }
        return Response(data, status=status.HTTP_200_OK)

class BPADashboardView(APIView):
    permission_classes = [IsAuthenticated]  # Sesuaikan jika perlu hanya untuk BPA

    def get(self, request):
        total_alumni = AlumniProfile.objects.count()
        total_events = Event.objects.count()
        total_donations = Donation.objects.aggregate(total=Sum('amount'))['total'] or 0
        total_usages = Usage.objects.aggregate(total=Sum('amount'))['total'] or 0
        balance = total_donations - total_usages

        # Hitung partisipasi alumni: jumlah pendaftaran per event
        alumni_participation_qs = EventRegistration.objects.values('event__title').annotate(count=Count('id')).order_by('event__title')
        alumni_participation = [
            {"label": item["event__title"], "count": item["count"]}
            for item in alumni_participation_qs
        ]

        # Ambil data penggunaan dana
        usage_data_qs = Usage.objects.all().values("description", "amount", "date").order_by("-date")
        usage_data = list(usage_data_qs)

        data = {
            "total_alumni": total_alumni,
            "total_events": total_events,
            "total_donations": total_donations,
            "total_usages": total_usages,
            "balance": balance,
            "usage_data": usage_data,
            "alumni_participation": alumni_participation,
        }
        return Response(data)
    
# 1. Audit Aktivitas: ViewSet untuk log audit
class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint untuk melihat log aktivitas (audit activity).
    Hanya dapat diakses oleh BPA.
    """
    queryset = AuditLog.objects.all().order_by('-timestamp')
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsBPA]

# 2. Laporan Audit: View untuk laporan audit (opsional, sama dengan AuditLogViewSet)
class AuditReportView(APIView):
    """
    Endpoint untuk BPA mengambil laporan audit.
    """
    permission_classes = [IsAuthenticated, IsBPA]

    def get(self, request):
        logs = AuditLog.objects.all().order_by('-timestamp')
        serializer = AuditLogSerializer(logs, many=True, context={'request': request})
        return Response(serializer.data)

# 3. Pengawasan Event: View untuk menampilkan event beserta jumlah pendaftar
class EventSupervisionView(APIView):
    """
    Endpoint untuk BPA melihat daftar event beserta jumlah pendaftar.
    """
    permission_classes = [IsAuthenticated, IsBPA]

    def get(self, request):
        events = Event.objects.annotate(registration_count=Count('registrations')).order_by('-start_date')
        event_data = []
        for event in events:
            event_data.append({
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "start_date": event.start_date,
                "end_date": event.end_date,
                "location": event.location,
                "registration_count": event.registration_count,
            })
        return Response(event_data)
    

class StatisticsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        total_event_participation = EventRegistration.objects.count()
        total_donations = Donation.objects.aggregate(total=Sum('amount'))['total'] or 0
        total_engagement = Feedback.objects.count()
        data = {
            "participation": total_event_participation,
            "donations": total_donations,
            "engagement": total_engagement,
        }
        return Response(data)
    
class DireksiViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Direksi.objects.all()
    serializer_class = DireksiSerializer

class BPAViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BPA.objects.all()
    serializer_class = BPASerializer