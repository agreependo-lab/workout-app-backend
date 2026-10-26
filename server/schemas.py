from marshmallow import Schema, ValidationError, fields, validate, validates_schema


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    category = fields.Str(
        required=True,
        validate=validate.OneOf(["strength", "cardio", "flexibility", "balance"]),
    )
    equipment_needed = fields.Bool(load_default=False)


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(allow_none=True, validate=validate.Range(min=1, max=1000))
    sets = fields.Int(allow_none=True, validate=validate.Range(min=1, max=100))
    duration_seconds = fields.Int(allow_none=True, validate=validate.Range(min=1, max=86400))
    exercise = fields.Nested(ExerciseSchema, dump_only=True)

    @validates_schema
    def require_one_measure(self, data, **kwargs):
        if not any(data.get(k) for k in ("reps", "sets", "duration_seconds")):
            raise ValidationError(
                "Provide at least one of reps, sets, or duration_seconds.",
                field_name="_schema",
            )


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True, validate=validate.Range(min=1, max=1440))
    notes = fields.Str(allow_none=True, validate=validate.Length(max=500))
    workout_exercises = fields.List(fields.Nested(WorkoutExerciseSchema), dump_only=True)


class ExerciseDetailSchema(ExerciseSchema):
    workouts = fields.List(
        fields.Nested(WorkoutSchema, only=("id", "date", "duration_minutes", "notes")),
        dump_only=True,
    )


exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
exercise_detail_schema = ExerciseDetailSchema()
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True, exclude=("workout_exercises",))
workout_exercise_schema = WorkoutExerciseSchema()