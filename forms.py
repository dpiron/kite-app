from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class SpotForm(FlaskForm):
    name = StringField("Spot name", validators=[DataRequired()])
    lat = StringField("Latitude", validators=[DataRequired()])
    long = StringField("Longitude", validators=[DataRequired()])
    offside = StringField("Offside", validators=[DataRequired()])
    submit = SubmitField("Submit")