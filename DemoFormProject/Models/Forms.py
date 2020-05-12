from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms import Form, BooleanField, PasswordField
from wtforms import TextField, TextAreaField, SelectField, DateField,RadioField
from wtforms import validators, ValidationError

from wtforms.validators import DataRequired
from wtforms.validators import InputRequired




class ExpandForm(FlaskForm):
    submit1 = SubmitField('Expand')
    name="Expand" 
    value="Expand"

class CollapseForm(FlaskForm):
    submit2 = SubmitField('Collapse')
    name="Collapse" 
    value="Collapse"

class QueryForm(FlaskForm):
    category   = SelectField('Category Name:  ' , validators = [DataRequired()],choices = [("robbery" , "robbery"),("vandalism","vandalism"),('disorderly conduct','disorderly conduct'),('fraud','fraud'),('arson','arson'),('embezzlement','embezzlement'),('gambling','gambling'),('prostitution','prostitution')])
    daymonthchosen =  RadioField('Choose one of:' , validators = [DataRequired] , choices=[('Day', 'Day'), ('Month', 'Month')])
    submit = SubmitField('Submit')