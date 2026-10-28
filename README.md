# Task Management API — GraphQL Edition

A simple Task Management API built with **Django + Graphene**, as a companion
to the tutorial on [mariomthree.com](https://mariomthree.com).

This is the GraphQL version of the same project built with Django REST Framework
in a previous tutorial — so you can compare both approaches side by side.

## Features
- Single `/graphql/` endpoint with GraphiQL playground
- Queries: `allTasks` (with optional status filter), `taskById`
- Mutations: `createTask`, `updateTaskStatus` (with validation), `deleteTask`
- 7 automated tests

## Quick Start
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
Open http://127.0.0.1:8000/graphql/ and try:
```graphql
mutation {
  createTask(title: "My first task") {
    ok
    task { id title status }
  }
}
```

## Run Tests
```bash
python manage.py test
```

## Related Articles
- [GraphQL vs REST: When to Choose Each](https://mariomthree.com/graphql-vs-rest/)
- [Building a RESTful API with Python](https://mariomthree.com/building-a-restful-api-with-python-creating-a-simple-task-management/)
