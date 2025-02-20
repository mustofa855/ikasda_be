from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from .models import User, AlumniProfile, News, Event, Donation, Feedback

# Karena kita menggunakan custom User, kita bisa membuat custom UserAdmin
class CustomUserAdmin(UserAdmin):
    model = User
    # Menampilkan field yang diinginkan di daftar admin
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    # Mengatur field yang tampil saat melihat detail user
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'phone')}),
    )
    # Untuk form penambahan user baru
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'phone')}),
    )

# Mendaftarkan model ke admin
admin.site.register(User, CustomUserAdmin)
admin.site.register(AlumniProfile)
admin.site.register(News)
admin.site.register(Event)
admin.site.register(Donation)
admin.site.register(Feedback)
