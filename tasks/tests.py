"""Automated tests for the GraphQL Task API."""
import json
from django.test import TestCase, Client
from .models import Task


class GraphQLTaskAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.task = Task.objects.create(title="Test task", description="A test")

    def query(self, q):
        response = self.client.post(
            "/graphql/", data=json.dumps({"query": q}),
            content_type="application/json",
        )
        return json.loads(response.content)

    def test_query_all_tasks(self):
        data = self.query("{ allTasks { title status } }")
        self.assertEqual(data["data"]["allTasks"][0]["title"], "Test task")
        self.assertEqual(data["data"]["allTasks"][0]["status"], "PENDING")

    def test_query_task_by_id(self):
        data = self.query(f'{{ taskById(id: {self.task.id}) {{ title }} }}')
        self.assertEqual(data["data"]["taskById"]["title"], "Test task")

    def test_create_task_mutation(self):
        data = self.query('''
            mutation { createTask(title: "New task") { ok task { title } } }
        ''')
        self.assertTrue(data["data"]["createTask"]["ok"])
        self.assertEqual(Task.objects.count(), 2)

    def test_update_status_mutation(self):
        data = self.query(f'''
            mutation {{ updateTaskStatus(id: {self.task.id}, status: "done") {{ ok task {{ status }} }} }}
        ''')
        self.assertTrue(data["data"]["updateTaskStatus"]["ok"])
        self.assertEqual(data["data"]["updateTaskStatus"]["task"]["status"], "DONE")

    def test_invalid_status_returns_error_message(self):
        data = self.query(f'''
            mutation {{ updateTaskStatus(id: {self.task.id}, status: "flying") {{ ok message }} }}
        ''')
        self.assertFalse(data["data"]["updateTaskStatus"]["ok"])
        self.assertIn("Invalid status", data["data"]["updateTaskStatus"]["message"])

    def test_delete_task_mutation(self):
        data = self.query(f'mutation {{ deleteTask(id: {self.task.id}) {{ ok }} }}')
        self.assertTrue(data["data"]["deleteTask"]["ok"])
        self.assertEqual(Task.objects.count(), 0)

    def test_client_chooses_fields(self):
        """The core GraphQL promise: response contains ONLY requested fields."""
        data = self.query("{ allTasks { title } }")
        task = data["data"]["allTasks"][0]
        self.assertIn("title", task)
        self.assertNotIn("description", task)
        self.assertNotIn("status", task)
