# core/permissions.py
from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'

# core/permissions.py
from rest_framework import permissions

class IsAlumni(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'alumni'

class IsDireksi(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'direksi'

class IsBPA(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'bpa'
    
# core/permissions.py

class IsDireksiOrReadOnly(permissions.BasePermission):
    """
    Mengizinkan akses baca (read-only) untuk semua user,
    namun operasi tulis (create, update, delete) hanya untuk user dengan role 'direksi'.
    """
    def has_permission(self, request, view):
        # Jika metode yang digunakan termasuk safe (GET, HEAD, OPTIONS), izinkan
        if request.method in permissions.SAFE_METHODS:
            return True
        # Untuk metode non-safe, hanya izinkan jika user terautentikasi dan role-nya 'direksi'
        return request.user and request.user.is_authenticated and request.user.role == 'direksi'

