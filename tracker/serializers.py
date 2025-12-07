from rest_framework import serializers
from .models import Project, Task
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class ProjectSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'owner', 'created_at', 'updated_at']

    def create(self, validated_data):
        # owner injected from view
        return Project.objects.create(**validated_data)


class TaskSerializer(serializers.ModelSerializer):
    assignee_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    assignee = serializers.SerializerMethodField(read_only=True)
    project_id = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = Task
        fields = [
            'id', 'project_id', 'title', 'description', 'status',
            'priority', 'due_date', 'assignee_id', 'assignee',
            'created_at', 'updated_at'
        ]

    def get_assignee(self, obj):
        return obj.assignee.username if obj.assignee else None

    def validate_priority(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Priority must be between 1 (highest) and 5 (lowest).")
        return value

    def validate(self, attrs):
        # if status == done and due_date in future -> error
        status = attrs.get('status', None)
        due_date = attrs.get('due_date', None)
        if status == 'done' and due_date:
            if due_date > timezone.localdate():
                raise serializers.ValidationError({'due_date': "A task marked as done cannot have a future due date."})
        return attrs

    def create(self, validated_data):
        assignee_id = validated_data.pop('assignee_id', None)
        project_id = validated_data.pop('project_id')
        # fetch project (view will have checked permission too)
        project = Project.objects.get(id=project_id)
        if assignee_id:
            try:
                assignee = User.objects.get(id=assignee_id)
            except User.DoesNotExist:
                raise serializers.ValidationError({'assignee_id': 'No user with this id.'})
        else:
            assignee = None
        task = Task.objects.create(project=project, assignee=assignee, **validated_data)
        return task
