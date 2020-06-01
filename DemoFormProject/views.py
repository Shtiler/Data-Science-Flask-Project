"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from DemoFormProject import app
from DemoFormProject.Models.LocalDatabaseRoutines import create_LocalDatabaseServiceRoutines
from flask_bootstrap import Bootstrap
bootstrap = Bootstrap(app)
from datetime import datetime
from flask import render_template, redirect, request

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import calendar
import json 
import requests
import base64from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvasfrom matplotlib.figure import Figure
import io
from os import path
from flask   import Flask, render_template, flash, request
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from wtforms import TextField, TextAreaField, SubmitField, SelectField, DateField
from wtforms import ValidationError
from DemoFormProject.Models.Forms import ExpandForm
from DemoFormProject.Models.Forms import CollapseForm
from DemoFormProject.Models.QueryFormStructure import QueryFormStructure 
from DemoFormProject.Models.QueryFormStructure import LoginFormStructure 
from DemoFormProject.Models.QueryFormStructure import UserRegistrationFormStructure 
from DemoFormProject.Models.Forms import QueryForm

db_Functions = create_LocalDatabaseServiceRoutines() 


@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )


@app.route('/Album')
def Album():
    """Renders the about page."""
    return render_template(
        'PictureAlbum.html',
        title='Pictures',
        year=datetime.now().year,
        message='Welcome to my picture album'
    )


@app.route('/Query' , methods = ['GET' , 'POST'])
def Query():

    form1 = QueryForm()
    chart = '/static/pics/contactpic.png'

   
    dfSF = pd.read_csv(path.join(path.dirname(__file__), 'static/data/SF.csv'), encoding="ISO-8859-1")
    dfBoston = pd.read_csv(path.join(path.dirname(__file__), 'static/data/BostonData.csv'), encoding="ISO-8859-1")
    chosencategory = form1.category.data
    daymonthchosen = form1.daymonthchosen.data

    if request.method == 'POST':
        categories_boston = list(set(dfBoston["OFFENSE_CODE_GROUP"].tolist()))
        i = 0
        for item in categories_boston:
            categories_boston[i] = item.lower()
            i = i+1
        categories_SF = list(set(dfSF["Category"].tolist()))
        i = 0
        for item in categories_SF:
            categories_SF[i] = item.lower()
            i = i+1
        commonlist = []
        for item in categories_SF:
            if item in categories_boston:
                commonlist.append(item)
        dfSF = dfSF[["Category","Date"]]
        dfSF["Date"] = pd.to_datetime(dfSF["Date"])
        dfSF["Month"] = dfSF["Date"].dt.month_name()
        dfSF["Day"] = dfSF["Date"].dt.day_name()
        dfSF = dfSF.drop("Date" , 1)
        dfSF["Category"] = dfSF["Category"].apply(lambda x:x.lower())
        dfBoston = dfBoston[["OFFENSE_CODE_GROUP","OCCURRED_ON_DATE"]]
        dfBoston["OCCURRED_ON_DATE"] = pd.to_datetime(dfBoston["OCCURRED_ON_DATE"])
        dfBoston["Day"] = dfBoston["OCCURRED_ON_DATE"].dt.day_name()
        dfBoston["Month"] = dfBoston["OCCURRED_ON_DATE"].dt.month_name()
        dfBoston = dfBoston.drop("OCCURRED_ON_DATE" , 1)
        dfBoston = dfBoston.rename(columns = {"OFFENSE_CODE_GROUP" : "Category"})
        dfBoston["Category"] = dfBoston["Category"].apply(lambda x:x.lower())
        dfSF = dfSF[dfSF["Category"].isin(commonlist)]
        dfBoston = dfBoston[dfBoston["Category"].isin(commonlist)]
        dfBoston = dfBoston[dfBoston.Category == chosencategory]
        dfSF = dfSF[dfSF.Category == chosencategory]
        if daymonthchosen == "Day" : 
            dfBoston = dfBoston.drop("Month",1)
            dfSF = dfSF.drop("Month",1)
            dfBoston = dfBoston.groupby("Day").size().to_frame(name = 'Boston')
            dfSF = dfSF.groupby("Day").size().to_frame(name = 'SF')
            dfSF = dfSF.reindex(calendar.day_name)
            dfBoston = dfBoston.reindex(calendar.day_name)
            dfSF = dfSF.dropna()
            dfBoston = dfBoston.dropna()
        else :
            dfBoston = dfBoston.drop("Day",1)
            dfBoston = dfBoston.groupby("Month").size().to_frame(name = 'Boston')
            dfSF = dfSF.drop("Day",1)
            dfSF = dfSF.groupby("Month").size().to_frame(name = 'SF')
            dfSF = dfSF.reindex(calendar.month_name)
            dfBoston = dfBoston.reindex(calendar.month_name)
            dfSF = dfSF.dropna()
            dfBoston = dfBoston.dropna()
        dfCombo = pd.merge(dfSF,dfBoston,on = daymonthchosen)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        fig.subplots_adjust(bottom=0.4)
        dfCombo.plot(kind = "bar", ax = ax)
        chart = plot_to_img(fig)
    return render_template(
        'Query.html',
        form1 = form1,
        chart = chart
    )

# -------------------------------------------------------
# Register new user page
# -------------------------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def Register():
    form = UserRegistrationFormStructure(request.form)

    if (request.method == 'POST' and form.validate()):
        if (not db_Functions.IsUserExist(form.username.data)):
            db_Functions.AddNewUser(form)
            db_table = ""

            flash('Thanks for registering new user - '+ form.FirstName.data + " " + form.LastName.data )
            # Here you should put what to do (or were to go) if registration was good
        else:
            flash('Error: User with this Username already exist ! - '+ form.username.data)
            form = UserRegistrationFormStructure(request.form)

    return render_template(
        'register.html', 
        form=form, 
        title='Register New User',
        year=datetime.now().year,
        repository_name='Pandas',
        )

# -------------------------------------------------------
# Login page
# This page is the filter before the data analysis
# -------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def Login():
    form = LoginFormStructure(request.form)

    if (request.method == 'POST' and form.validate()):
        if (db_Functions.IsLoginGood(form.username.data, form.password.data)):
            flash('Login approved!')
            return redirect('Query')
        else:
            flash('Error in - Username and/or password')
   
    return render_template(
        'login.html', 
        form=form, 
        title='Login to data analysis',
        year=datetime.now().year,
        repository_name='Pandas',
        )
@app.route('/Data')
def Data():
    """Renders the about page."""
    return render_template(
        'Data.html',
        title='Data',
        year=datetime.now().year,
        message='Your application description page.'
    )
@app.route('/BostonData', methods = ['GET' , 'POST'])
def BostonData():
    """Renders the about page."""
    form1 = ExpandForm()
    form2 = CollapseForm()
    df = pd.read_csv(path.join(path.dirname(__file__), 'static/data/Boston.csv'), encoding="ISO-8859-1")
    df = df.set_index(['YEAR'])
    df.sort_values('YEAR', ascending=True)
    df = df.fillna('N')
    df = df.drop(columns=['INCIDENT_NUMBER', 'OFFENSE_CODE', 'Lat', 'Long','UCR_PART'])
    raw_data_table = ''
    if request.method == 'POST':
        if request.form['action'] == 'Expand' and form1.validate_on_submit():
            raw_data_table = df.head(120).to_html(classes = 'table table-hover')
        if request.form['action'] == 'Collapse' and form2.validate_on_submit():
            raw_data_table = ''
    return render_template(
        'BostonData.html',
        title='BostonData',
        year=datetime.now().year,
        message='Your application description page.',
        raw_data_table = raw_data_table,
        form1 = form1,
        form2 = form2

    )
@app.route('/SanFranciscoData' , methods = ['GET' , 'POST'])
def SanFranciscoData():
    """Renders the about page."""
    form1 = ExpandForm()
    form2 = CollapseForm()
    df = pd.read_csv(path.join(path.dirname(__file__), 'static\\Data\\SanFran.csv'))
    raw_data_table = ''
    if request.method == 'POST':
        if request.form['action'] == 'Expand' and form1.validate_on_submit():
            raw_data_table = df.head(120).to_html(classes = 'table table-hover')
        if request.form['action'] == 'Collapse' and form2.validate_on_submit():
            raw_data_table = ''
    return render_template(
        'SanFranciscoData.html',
        title='SanFranciscoData',
        form1 = form1,
        form2 = form2,
        year=datetime.now().year,
        message='Your application description page.',
        raw_data_table = raw_data_table
    )



def plot_to_img(fig):    pngImage = io.BytesIO()    FigureCanvas(fig).print_png(pngImage)    pngImageB64String = "data:image/png;base64,"    pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')    return pngImageB64String



