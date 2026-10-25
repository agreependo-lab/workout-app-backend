from datetime import date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

db = SQLAlchemy()


class Exercise(db.Model):
    __tablename__ = "exercises"

    __table_args__ = (
        db.CheckConstraint("length(name) >= 2", name="ck_exercise_name_length"),
        db.CheckConstraint(
            "category IN ('strength', 'cardio', 'flexibility', 'balance')",
            name="ck_exercise_category",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    category = db.Column(db.String, nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    workout_exercises = db.relationship(
        "WorkoutExercise", back_populates="exercise", cascade="all, delete-orphan"
    )
    workouts = db.relationship(
        "Workout",
        secondary="workout_exercises",
        back_populates="exercises",
        viewonly=True,
    )

    @validates("name")
    def validate_name(self, key, value):
        if not isinstance(value, str) or len(value.strip()) < 2:
            raise ValueError("Exercise name must be at least 2 characters long.")
        return value.strip()

    @validates("category")
    def validate_category(self, key, value):
        allowed = ("strength", "cardio", "flexibility", "balance")
        if value not in allowed:
            raise ValueError(f"Category must be one of: {', '.join(allowed)}.")
        return value

    def __repr__(self):
        return f"<Exercise {self.id}: {self.name}>"


class Workout(db.Model):
    __tablename__ = "workouts"

    __table_args__ = (
        db.CheckConstraint("duration_minutes > 0", name="ck_workout_duration_positive"),
    )

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

    workout_exercises = db.relationship(
        "WorkoutExercise", back_populates="workout", cascade="all, delete-orphan"
    )
    exercises = db.relationship(
        "Exercise",
        secondary="workout_exercises",
        back_populates="workouts",
        viewonly=True,
    )

    @validates("date")
    def validate_date(self, key, value):
        if not isinstance(value, date):
            raise ValueError("Workout date must be a valid date.")
        return value

    @validates("duration_minutes")
    def validate_duration(self, key, value):
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise ValueError("Workout duration must be a positive whole number of minutes.")
        return value

    def __repr__(self):
        return f"<Workout {self.id}: {self.date}>"


class WorkoutExercise(db.Model):
    __tablename__ = "workout_exercises"

    __table_args__ = (
        db.CheckConstraint("reps IS NULL OR reps > 0", name="ck_we_reps_positive"),
        db.CheckConstraint("sets IS NULL OR sets > 0", name="ck_we_sets_positive"),
        db.CheckConstraint(
            "duration_seconds IS NULL OR duration_seconds > 0",
            name="ck_we_duration_positive",
        ),
        db.UniqueConstraint("workout_id", "exercise_id", name="uq_workout_exercise"),
    )

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey("workouts.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)
    reps = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)

    workout = db.relationship("Workout", back_populates="workout_exercises")
    exercise = db.relationship("Exercise", back_populates="workout_exercises")

    @validates("reps", "sets", "duration_seconds")
    def validate_positive(self, key, value):
        if value is not None and (
            not isinstance(value, int) or isinstance(value, bool) or value <= 0
        ):
            raise ValueError(f"{key} must be a positive whole number.")
        return value

    def __repr__(self):
        return f"<WorkoutExercise workout={self.workout_id} exercise={self.exercise_id}>"