"""GraphQL schema for the Task Management API.

This is the heart of the tutorial: instead of DRF serializers + views + routers,
GraphQL uses Types (what data looks like), Queries (reads) and Mutations (writes).
"""
import graphene
from graphene_django import DjangoObjectType

from .models import Task


# ---------------------------------------------------------------------------
# 1. TYPE — the GraphQL representation of our Django model
#    (equivalent to a DRF Serializer)
# ---------------------------------------------------------------------------
class TaskType(DjangoObjectType):
    class Meta:
        model = Task
        fields = ("id", "title", "description", "status", "created_at", "updated_at")


# ---------------------------------------------------------------------------
# 2. QUERIES — how clients READ data
#    (equivalent to DRF list/retrieve views)
# ---------------------------------------------------------------------------
class Query(graphene.ObjectType):
    all_tasks = graphene.List(
        TaskType,
        status=graphene.String(required=False),
        description="Retrieve all tasks, optionally filtered by status.",
    )
    task_by_id = graphene.Field(
        TaskType,
        id=graphene.ID(required=True),
        description="Retrieve a single task by its ID.",
    )

    def resolve_all_tasks(root, info, status=None):
        queryset = Task.objects.all()
        if status:
            queryset = queryset.filter(status=status.upper())
        return queryset

    def resolve_task_by_id(root, info, id):
        try:
            return Task.objects.get(pk=id)
        except Task.DoesNotExist:
            return None


# ---------------------------------------------------------------------------
# 3. MUTATIONS — how clients WRITE data
#    (equivalent to DRF create/update/destroy views)
# ---------------------------------------------------------------------------
class CreateTask(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String(required=False)

    task = graphene.Field(TaskType)
    ok = graphene.Boolean()

    def mutate(root, info, title, description=""):
        task = Task.objects.create(title=title, description=description)
        return CreateTask(task=task, ok=True)


class UpdateTaskStatus(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        status = graphene.String(required=True)

    task = graphene.Field(TaskType)
    ok = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, status):
        status = status.upper()
        valid = [choice[0] for choice in Task.Status.choices]
        if status not in valid:
            return UpdateTaskStatus(
                task=None, ok=False,
                message=f"Invalid status. Valid options: {', '.join(valid)}",
            )
        try:
            task = Task.objects.get(pk=id)
        except Task.DoesNotExist:
            return UpdateTaskStatus(task=None, ok=False, message="Task not found.")
        task.status = status
        task.save()
        return UpdateTaskStatus(task=task, ok=True, message="Status updated.")


class DeleteTask(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id):
        deleted, _ = Task.objects.filter(pk=id).delete()
        if deleted:
            return DeleteTask(ok=True, message="Task deleted.")
        return DeleteTask(ok=False, message="Task not found.")


class Mutation(graphene.ObjectType):
    create_task = CreateTask.Field()
    update_task_status = UpdateTaskStatus.Field()
    delete_task = DeleteTask.Field()


# ---------------------------------------------------------------------------
# 4. SCHEMA — ties everything together
# ---------------------------------------------------------------------------
schema = graphene.Schema(query=Query, mutation=Mutation)
