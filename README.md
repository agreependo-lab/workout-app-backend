# Workout Application Backend

A Flask REST API for a workout tracking app used by personal trainers. Built with Flask, SQLAlchemy, Flask-Migrate and Marshmallow.

## Description
Trainers can create workouts and reusable exercises, then add exercises to workouts with sets, reps, or duration. The API has validations at three levels: database table constraints, model validations, and Marshmallow schema validations.

## Installation
```bash
pipenv install --dev
pipenv shell
export FLASK_APP=server/app.py
flask db init
flask db migrate -m "Initial migration"
flask db upgrade head
python server/seed.py
```

## Run
```bash
flask run -p 5555
```
The API runs at http://127.0.0.1:5555

## Tests
```bash
pytest server -v
```

## Endpoints
| Method | Endpoint | Description |
|---|---|---|
| GET | /workouts | List all workouts |
| GET | /workouts/<id> | Show one workout with its exercises (sets, reps, duration) |
| POST | /workouts | Create a workout (`date`, `duration_minutes`, optional `notes`) |
| DELETE | /workouts/<id> | Delete a workout and its exercise links |
| GET | /exercises | List all exercises |
| GET | /exercises/<id> | Show one exercise and the workouts it appears in |
| POST | /exercises | Create an exercise (`name`, `category`, optional `equipment_needed`) |
| DELETE | /exercises/<id> | Delete an exercise and its workout links |
| POST | /workouts/<workout_id>/exercises/<exercise_id>/workout_exercises | Add an exercise to a workout (`reps`, `sets`, `duration_seconds`) |

## Validations
- **Table constraints:** unique exercise names, NOT NULL columns, CHECK constraints (positive duration, reps, sets; valid category), unique workout/exercise pair.
- **Model validations:** `@validates` on exercise name and category, workout date and duration, and reps, sets and duration_seconds.
- **Schema validations:** Marshmallow `Length`, `Range` and `OneOf` validators, plus a schema-level rule requiring at least one of reps, sets or duration.

## Dependencies
See the `Pipfile`.