import pytest

from app import create_app
from models import Exercise, Workout, WorkoutExercise, db

@pytest.fixture
def client():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def make_workout(client, **overrides):
    body = {"date": "2026-10-25", "duration_minutes": 40, "notes": "Test"}
    body.update(overrides)
    return client.post("/workouts", json=body)


def make_exercise(client, **overrides):
    body = {"name": "Lunge", "category": "strength", "equipment_needed": False}
    body.update(overrides)
    return client.post("/exercises", json=body)


# ---------- Workouts ----------
def test_create_and_list_workouts(client):
    assert make_workout(client).status_code == 201
    res = client.get("/workouts")
    assert res.status_code == 200 and len(res.get_json()) == 1


def test_get_workout_includes_exercises(client):
    wid = make_workout(client).get_json()["id"]
    eid = make_exercise(client).get_json()["id"]
    client.post(f"/workouts/{wid}/exercises/{eid}/workout_exercises", json={"sets": 3, "reps": 10})
    data = client.get(f"/workouts/{wid}").get_json()
    assert data["workout_exercises"][0]["exercise"]["name"] == "Lunge"
    assert data["workout_exercises"][0]["sets"] == 3


def test_workout_not_found(client):
    assert client.get("/workouts/999").status_code == 404
    assert client.delete("/workouts/999").status_code == 404


def test_delete_workout(client):
    wid = make_workout(client).get_json()["id"]
    assert client.delete(f"/workouts/{wid}").status_code == 200
    assert client.get(f"/workouts/{wid}").status_code == 404


def test_workout_schema_validation_negative_duration(client):
    assert make_workout(client, duration_minutes=-5).status_code == 400


def test_workout_schema_validation_bad_date(client):
    assert make_workout(client, date="not-a-date").status_code == 400


def test_workout_missing_fields(client):
    assert client.post("/workouts", json={}).status_code == 400


def test_workout_model_validation():
    with pytest.raises(ValueError):
        Workout(duration_minutes=0)


# ---------- Exercises ----------
def test_create_and_list_exercises(client):
    assert make_exercise(client).status_code == 201
    assert len(client.get("/exercises").get_json()) == 1


def test_get_exercise_shows_workouts(client):
    wid = make_workout(client).get_json()["id"]
    eid = make_exercise(client).get_json()["id"]
    client.post(f"/workouts/{wid}/exercises/{eid}/workout_exercises", json={"reps": 8})
    data = client.get(f"/exercises/{eid}").get_json()
    assert len(data["workouts"]) == 1


def test_exercise_unique_name_constraint(client):
    make_exercise(client)
    assert make_exercise(client).status_code == 400


def test_exercise_invalid_category(client):
    assert make_exercise(client, category="swimming").status_code == 400


def test_exercise_model_validation():
    with pytest.raises(ValueError):
        Exercise(name="A")
    with pytest.raises(ValueError):
        Exercise(name="Okay", category="nonsense")


def test_delete_exercise(client):
    eid = make_exercise(client).get_json()["id"]
    assert client.delete(f"/exercises/{eid}").status_code == 200
    assert client.get(f"/exercises/{eid}").status_code == 404


# ---------- Workout exercises ----------
def test_add_exercise_requires_measure(client):
    wid = make_workout(client).get_json()["id"]
    eid = make_exercise(client).get_json()["id"]
    res = client.post(f"/workouts/{wid}/exercises/{eid}/workout_exercises", json={})
    assert res.status_code == 400


def test_add_exercise_rejects_negative_reps(client):
    wid = make_workout(client).get_json()["id"]
    eid = make_exercise(client).get_json()["id"]
    res = client.post(f"/workouts/{wid}/exercises/{eid}/workout_exercises", json={"reps": -3})
    assert res.status_code == 400


def test_add_duplicate_exercise_to_workout(client):
    wid = make_workout(client).get_json()["id"]
    eid = make_exercise(client).get_json()["id"]
    url = f"/workouts/{wid}/exercises/{eid}/workout_exercises"
    assert client.post(url, json={"reps": 5}).status_code == 201
    assert client.post(url, json={"reps": 5}).status_code == 400


def test_add_exercise_not_found(client):
    assert client.post("/workouts/1/exercises/1/workout_exercises", json={"reps": 5}).status_code == 404


def test_delete_workout_cascades_links(client):
    wid = make_workout(client).get_json()["id"]
    eid = make_exercise(client).get_json()["id"]
    client.post(f"/workouts/{wid}/exercises/{eid}/workout_exercises", json={"reps": 5})
    client.delete(f"/workouts/{wid}")
    assert WorkoutExercise.query.count() == 0