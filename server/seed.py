from datetime import date

from app import app
from models import Exercise, Workout, WorkoutExercise, db

with app.app_context():
    print("Clearing old data...")
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()

    print("Seeding exercises...")
    squat = Exercise(name="Squat", category="strength", equipment_needed=True)
    pushup = Exercise(name="Push-up", category="strength", equipment_needed=False)
    running = Exercise(name="Running", category="cardio", equipment_needed=False)
    plank = Exercise(name="Plank", category="balance", equipment_needed=False)
    yoga = Exercise(name="Yoga Flow", category="flexibility", equipment_needed=False)
    db.session.add_all([squat, pushup, running, plank, yoga])

    print("Seeding workouts...")
    w1 = Workout(date=date(2026, 10, 20), duration_minutes=45, notes="Leg day")
    w2 = Workout(date=date(2026, 10, 22), duration_minutes=30, notes="Cardio and core")
    w3 = Workout(date=date(2026, 10, 24), duration_minutes=60, notes="Full body")
    db.session.add_all([w1, w2, w3])
    db.session.commit()

    print("Linking exercises to workouts...")
    db.session.add_all(
        [
            WorkoutExercise(workout_id=w1.id, exercise_id=squat.id, sets=4, reps=10),
            WorkoutExercise(workout_id=w1.id, exercise_id=plank.id, sets=3, duration_seconds=60),
            WorkoutExercise(workout_id=w2.id, exercise_id=running.id, duration_seconds=1200),
            WorkoutExercise(workout_id=w2.id, exercise_id=plank.id, sets=2, duration_seconds=45),
            WorkoutExercise(workout_id=w3.id, exercise_id=pushup.id, sets=3, reps=15),
            WorkoutExercise(workout_id=w3.id, exercise_id=squat.id, sets=3, reps=12),
            WorkoutExercise(workout_id=w3.id, exercise_id=yoga.id, duration_seconds=600),
        ]
    )
    db.session.commit()
    print("Done seeding!")