1. Create migration

```
alembic revision --autogenerate -m "create conversation_thread and messages tables"
```

2. Apply migration

```
alembic upgrade head
```

3. Common Alembic commands

```
alembic current
alembic history
alembic downgrade -1
```
