from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now
import uuid


class User(AbstractUser):
    """Custom user model for email/password and social logins."""

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, blank=True, null=True)
    REQUIRED_FIELDS = []
    USERNAME_FIELD = "email"

    # Add related_name to avoid conflicts
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_set",  # Change to avoid conflict
        blank=True,
        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
        verbose_name="groups",
    )
    permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_set",  # Change to avoid conflict
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    def __str__(self):
        return self.email


class Game(models.Model):
    """Game model associated with a user."""

    STATUS_CHOICES = [
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="games")
    session_id = models.UUIDField(default=uuid.uuid4, unique=True)
    game_name = models.CharField(max_length=255, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_time = models.DateTimeField(default=now)
    fen_string = models.TextField(
        help_text="FEN string describing the initial board state and turn."
    )
    moves = models.JSONField(
        default=list, help_text="List of moves taken during the game."
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="in_progress"
    )
    locked = models.BooleanField(
        default=False, help_text="True if the game is locked for editing."
    )

    def __str__(self):
        return f"Game {self.game_name} (Session ID: {self.session_id}, Status: {self.status})"


class Move(models.Model):
    """Move model to track individual moves in a game."""

    game = models.ForeignKey(
        Game, on_delete=models.CASCADE, related_name="move_history"
    )
    timestamp = models.DateTimeField(default=now)
    move_notation = models.CharField(
        max_length=10, help_text="Chess-like notation for the move."
    )

    def __str__(self):
        return f"Move {self.move_notation} at {self.timestamp}"


class JWT(models.Model):
    """JWT tracking model for API interactions."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="jwts")
    token = models.TextField(help_text="JWT Token string.")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    revoked = models.BooleanField(
        default=False, help_text="True if the JWT has been revoked."
    )

    def __str__(self):
        return f"JWT for {self.user.email}, Active: {self.is_active}, Revoked: {self.revoked}"


class AuditLog(models.Model):
    """Audit log to track user actions."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="audit_logs")
    action = models.CharField(max_length=50, help_text="Login, Logout, API Call, etc.")
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} {self.action} at {self.timestamp}"
