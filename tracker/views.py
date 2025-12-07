from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.db.models import Q
from .models import Project, Task
from .serializers import ProjectSerializer, TaskSerializer
from django.utils import timezone

# Projects: create & list
class ProjectCreateView(generics.CreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class ProjectListView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Project.objects.filter(owner=self.request.user)
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(name__icontains=search)
        return qs

# Create Task in a Project — only project owner can create
class ProjectTaskCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        if project.owner != request.user:
            return Response({'detail': 'Only project owner can create tasks.'}, status=status.HTTP_403_FORBIDDEN)
        data = request.data.copy()
        data['project_id'] = project_id
        serializer = TaskSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)

# List Tasks with filters:
class TaskListView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Task.objects.filter(
            Q(project__owner=user) | Q(assignee=user)
        ).select_related('project', 'assignee')
        status_q = self.request.query_params.get('status')
        project_id = self.request.query_params.get('project_id')
        due_before = self.request.query_params.get('due_before')
        if status_q:
            qs = qs.filter(status=status_q)
        if project_id:
            qs = qs.filter(project__id=project_id)
        if due_before:
            qs = qs.filter(due_date__lte=due_before)
        return qs

# summary-view-anchor
class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # total projects
        total_projects = Project.objects.filter(owner=user).count()

        # total tasks in their projects
        total_tasks = Task.objects.filter(project__owner=user).count()

        # tasks grouped by status (only tasks in their projects)
        status_counts_qs = Task.objects.filter(project__owner=user).values('status').annotate(count=Count('id'))
        status_counts = {item['status']: item['count'] for item in status_counts_qs}

        # top 5 upcoming tasks (soonest due_date), status != done and due_date not null
        upcoming_qs = Task.objects.filter(
            project__owner=user,
        ).exclude(status='done').exclude(due_date__isnull=True).order_by('due_date')[:5]

        upcoming = TaskSerializer(upcoming_qs, many=True).data
        if not upcoming:
            upcoming = "No upcoming tasks!"

        data = {
            'total_projects': total_projects,
            'total_tasks': total_tasks,
            'tasks_by_status': status_counts,
            'top_5_upcoming': upcoming
        }
        return Response(data)
