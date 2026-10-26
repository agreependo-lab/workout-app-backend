from flask import Flask, jsonify, request
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import Exercise, Workout, WorkoutExercise, db
from schemas import (
    exercise_detail_schema,
    exercise_schema,
    exercises_schema,
    workout_exercise_schema,
    workout_schema,
    workouts_schema,
)

migrate = Migrate()


def create_app(config=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.json.compact = False
    if config:
        app.config.update(config)

    db.init_app(app)
    migrate.init_app(app, db)

    # ---------- Workouts ----------
    @app.route("/workouts", methods=["GET"])
    def get_workouts():
        workouts = Workout.query.order_by(Workout.date.desc()).all()
        return jsonify(workouts_schema.dump(workouts)), 200

    @app.route("/workouts/<int:id>", methods=["GET"])
    def get_workout(id):
        workout = db.session.get(Workout, id)
        if not workout:
            return jsonify({"error": "Workout not found"}), 404
        return jsonify(workout_schema.dump(workout)), 200

    @app.route("/workouts", methods=["POST"])
    def create_workout():
        try:
            data = workout_schema.load(request.get_json(silent=True) or {})
            workout = Workout(**data)
            db.session.add(workout)
            db.session.commit()
        except ValidationError as err:
            return jsonify({"errors": err.messages}), 400
        except (ValueError, IntegrityError) as err:
            db.session.rollback()
            return jsonify({"errors": [str(err)]}), 400
        return jsonify(workout_schema.dump(workout)), 201

    @app.route("/workouts/<int:id>", methods=["DELETE"])
    def delete_workout(id):
        workout = db.session.get(Workout, id)
        if not workout:
            return jsonify({"error": "Workout not found"}), 404
        db.session.delete(workout)
        db.session.commit()
        return jsonify({"message": "Workout deleted"}), 200

    # ---------- Exercises ----------
    @app.route("/exercises", methods=["GET"])
    def get_exercises():
        return jsonify(exercises_schema.dump(Exercise.query.all())), 200

    @app.route("/exercises/<int:id>", methods=["GET"])
    def get_exercise(id):
        exercise = db.session.get(Exercise, id)
        if not exercise:
            return jsonify({"error": "Exercise not found"}), 404
        return jsonify(exercise_detail_schema.dump(exercise)), 200

    @app.route("/exercises", methods=["POST"])
    def create_exercise():
        try:
            data = exercise_schema.load(request.get_json(silent=True) or {})
            exercise = Exercise(**data)
            db.session.add(exercise)
            db.session.commit()
        except ValidationError as err:
            return jsonify({"errors": err.messages}), 400
        except (ValueError, IntegrityError) as err:
            db.session.rollback()
            msg = "Exercise name must be unique" if isinstance(err, IntegrityError) else str(err)
            return jsonify({"errors": [msg]}), 400
        return jsonify(exercise_schema.dump(exercise)), 201

    @app.route("/exercises/<int:id>", methods=["DELETE"])
    def delete_exercise(id):
        exercise = db.session.get(Exercise, id)
        if not exercise:
            return jsonify({"error": "Exercise not found"}), 404
        db.session.delete(exercise)
        db.session.commit()
        return jsonify({"message": "Exercise deleted"}), 200

    # ---------- Add exercise to workout ----------
    @app.route(
        "/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises",
        methods=["POST"],
    )
    def add_exercise_to_workout(workout_id, exercise_id):
        workout = db.session.get(Workout, workout_id)
        exercise = db.session.get(Exercise, exercise_id)
        if not workout or not exercise:
            return jsonify({"error": "Workout or Exercise not found"}), 404
        try:
            data = workout_exercise_schema.load(request.get_json(silent=True) or {})
            link = WorkoutExercise(workout_id=workout_id, exercise_id=exercise_id, **data)
            db.session.add(link)
            db.session.commit()
        except ValidationError as err:
            return jsonify({"errors": err.messages}), 400
        except (ValueError, IntegrityError) as err:
            db.session.rollback()
            msg = (
                "This exercise is already in the workout"
                if isinstance(err, IntegrityError)
                else str(err)
            )
            return jsonify({"errors": [msg]}), 400
        return jsonify(workout_exercise_schema.dump(link)), 201

    return app


app = create_app()

if __name__ == "__main__":
    app.run(port=5555, debug=True)