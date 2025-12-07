from django.urls import path
from .views import (
    ProjectCreateView, ProjectListView,
    ProjectTaskCreateView, TaskListView, DashboardView
)

urlpatterns = [
    path('projects/', ProjectCreateView.as_view(), name='create-project'),
    path('projects/', ProjectListView.as_view(), name='list-projects'),  # note: will be same path but different method
    # To avoid same path class conflict, better to add combined view; simplest: use same path and let method dispatch by DRF Generic views.
    path('projects/<int:project_id>/tasks/', ProjectTaskCreateView.as_view(), name='project-create-task'),
    path('tasks/', TaskListView.as_view(), name='list-tasks'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
