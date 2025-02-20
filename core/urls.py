# core/urls.py
from django.urls import path, include
from rest_framework import routers
from .views import (
    AlumniGroupingView, AuditLogViewSet, AuditReportView, BPADashboardView, BPAViewSet, DireksiViewSet, EventSupervisionView, MyEventRegistrationListView, NewsViewSet, EventViewSet, DonationViewSet, FeedbackViewSet,
    RegisterView, EventRegistrationView, EventRegistrationListView,
    GalleryViewSet, AlumniProfileViewSet, StatisticsView, UsageViewSet, UserViewSet,
    DiscussionPostViewSet, DiscussionReplyViewSet, GalleryAlbumViewSet, GalleryImageViewSet,
    AlumniProfileUpdateView, DireksiDashboardView,
    StrategicDecisionViewSet,  # import view baru
)
from core import views

router = routers.DefaultRouter()
router.register(r'news', NewsViewSet)
router.register(r'events', EventViewSet)
router.register(r'donations', DonationViewSet, basename='donations')
router.register(r"usages", UsageViewSet)
router.register(r'feedbacks', FeedbackViewSet)
router.register(r'gallery', GalleryViewSet)
router.register(r'galleryalbums', GalleryAlbumViewSet)
router.register(r'galleryimages', GalleryImageViewSet)
router.register(r'alumni', AlumniProfileViewSet)
router.register(r'users', UserViewSet, basename='users')
router.register(r'discussions', DiscussionPostViewSet)
router.register(r'discussion-replies', DiscussionReplyViewSet)
router.register(r'strategic-decisions', StrategicDecisionViewSet, basename='strategic-decisions')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-logs')
router.register(r'direksi', DireksiViewSet, basename='direksi')
router.register(r'bpa', BPAViewSet, basename='bpa')


urlpatterns = [
    path('api/', include(router.urls)),
    path('api/direksi-dashboard/', DireksiDashboardView.as_view(), name='direksi-dashboard'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/event-registration/', EventRegistrationView.as_view(), name='event-registration'),
    path('api/event-registrations/', EventRegistrationListView.as_view(), name='event-registration-list'),
    path('api/my-event-registrations/', MyEventRegistrationListView.as_view(), name='my-event-registrations'),
    path('api/my-profile/', AlumniProfileUpdateView.as_view(), name='my-profile'),
    path('api/alumni-group/', AlumniGroupingView.as_view(), name='alumni_group'),
    path('api/request-verified/', views.request_verification, name='request-verification'),
    path('api/bpa-dashboard/', BPADashboardView.as_view(), name='bpa-dashboard'),
    path('api/audit-report/', AuditReportView.as_view(), name='audit-report'),
    path('api/event-supervision/', EventSupervisionView.as_view(), name='event-supervision'),
    path('api/statistics/', StatisticsView.as_view(), name='statistics'),
]
