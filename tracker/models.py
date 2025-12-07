
# Create your models here.
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['owner', 'name'], name='unique_project_name_per_owner')
        ]

    def __str__(self):
        return f"{self.name} ({self.owner})"


class Task(models.Model):
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.IntegerField()
    due_date = models.DateField(null=True, blank=True)
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        # priority must be 1..5
        if self.priority is None:
            raise ValidationError({'priority': "Priority must be between 1 (highest) and 5 (lowest)."})
        if not (1 <= self.priority <= 5):
            raise ValidationError({'priority': "Priority must be between 1 (highest) and 5 (lowest)."})

        # If status == done, due_date must not be in the future.
        if self.status == 'done' and self.due_date:
            if self.due_date > timezone.localdate():
                raise ValidationError({'due_date': "A task marked as done cannot have a future due date."})

    def save(self, *args, **kwargs):
        # Ensure model-level validation runs on save too
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.project})"
