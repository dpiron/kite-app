import requests
import datetime
from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap
from dateutil import parser
import operator
from flask_sqlalchemy import SQLAlchemy
import os
from forms import SpotForm

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
Bootstrap(app)


# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL",  "sqlite:///spots.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# spot_db = [
#     {
#         "name": "Oesterdam",
#         "lat": 51.475,
#         "long": 4.225,
#         "offside": 90
#     },
#     {
#         "name": "Grevelingendam",
#         "lat": 51.675,
#         "long": 4.125,
#         "offside": 0
#     }
# ]


# CONFIGURE TABLES
class Spot(db.Model):
    __tablename__ = "spots"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    lat = db.Column(db.Float)
    long = db.Column(db.Float)
    offside = db.Column(db.Integer)


db.create_all()


# Open weather
API_KEY = os.environ.get("API_KEY")
OWM_endpoint = "https://api.openweathermap.org/data/2.5/onecall"

# Arome
ARO_endpoint = "https://public.opendatasoft.com/api/records/1.0/search"


class Forecast:
    def __init__(self, name, lat, long, off):
        self.name = name
        self.off = off
        self.parameters_OWM = {
            "lat": lat,
            "lon": long,
            "exclude": "current,minutely,daily",
            "appid": API_KEY
        }

        self.response_OWM = requests.get(url=OWM_endpoint, params=self.parameters_OWM)
        self.response_OWM.raise_for_status()
        self.data_OWM = self.response_OWM.json()

        self.dt_OWM = [datetime.datetime.fromtimestamp(dt["dt"]) for dt in self.data_OWM["hourly"]]
        self.months_OWM = [hour.month for hour in self.dt_OWM]
        self.days_OWM = [hour.day for hour in self.dt_OWM]
        self.hours_OWM = [hour.hour for hour in self.dt_OWM]

        self.wind_speeds = [int(item["wind_speed"]) for item in self.data_OWM["hourly"]]
        self.wind_degs = [int(item["wind_deg"]) for item in self.data_OWM["hourly"]]
        self.wind_gusts = [int(item["wind_gust"]) for item in self.data_OWM["hourly"]]

        self.parameters_ARO = {
            "dataset": "arome-0025-sp1_sp2",
            "rows": 40,
            "sort": "-forecast",
            "geofilter.distance": f"{lat}, {long}, 1000",
        }

        self.response_ARO = requests.get(url=ARO_endpoint, params=self.parameters_ARO)
        self.response_ARO.raise_for_status()
        self.data_ARO = self.response_ARO.json()
        self.dt_ARO_str = [dt["fields"]["forecast"] for dt in self.data_ARO["records"]]
        self.dt_ARO = [datetime.datetime.fromtimestamp(datetime.datetime.timestamp(parser.parse(item))) for item in self.dt_ARO_str]
        self.months_ARO = [hour.month for hour in self.dt_ARO]
        self.days_ARO = [hour.day for hour in self.dt_ARO]
        self.hours_ARO = [hour.hour for hour in self.dt_ARO]
        self.wind_speeds_ARO = [int(dt["fields"]["wind_speed"]) for dt in self.data_ARO["records"]]
        i = 0
        k = 0
        for item in self.hours_ARO:
            if item == self.hours_OWM[0] and k == 0:
                k = i
            i = i+1
        self.hours_ARO_f = self.hours_ARO[k:]
        self.days_ARO_f = self.days_ARO[k:]
        self.months_ARO_f = self.months_ARO[k:]
        self.wind_speeds_ARO_f = self.wind_speeds_ARO[k:]
        i = 0
        self.wind_speeds_ARO_2 = []
        for item in self.hours_OWM:
            if i<(len(self.wind_speeds_ARO_f)):
                self.wind_speeds_ARO_2.append(self.wind_speeds_ARO_f[i])
            else:
                self.wind_speeds_ARO_2.append("-")
            i = i+1

        self.wind_speeds_cl = []
        self.wind_gusts_cl = []
        self.wind_speeds_ARO_2_cl = []
        for item in self.wind_speeds:
            if item < 1/9*40:
                self.wind_speeds_cl.append((item, "rgb(255,255,204)"))
            elif item < 2/9*40:
                self.wind_speeds_cl.append((item, "rgb(255,237,160)"))
            elif item < 3/9*40:
                self.wind_speeds_cl.append((item, "rgb(254,217,118)"))
            elif item < 4/9*40:
                self.wind_speeds_cl.append((item, "rgb(254,178,76)"))
            elif item < 5/9*40:
                self.wind_speeds_cl.append((item, "rgb(253,141,60)"))
            elif item < 6/9*40:
                self.wind_speeds_cl.append((item, "rgb(252,78,42)"))
            elif item < 7/9*40:
                self.wind_speeds_cl.append((item, "rgb(227,26,28)"))
            elif item < 8/9*40:
                self.wind_speeds_cl.append((item, "rgb(189,0,38)"))
            else:
                self.wind_speeds_cl.append((item, "rgb(128,0,38)"))

        for item in self.wind_gusts:
            if item < 1/9*40:
                self.wind_gusts_cl.append((item, "rgb(255,255,204)"))
            elif item < 2/9*40:
                self.wind_gusts_cl.append((item, "rgb(255,237,160)"))
            elif item < 3/9*40:
                self.wind_gusts_cl.append((item, "rgb(254,217,118)"))
            elif item < 4/9*40:
                self.wind_gusts_cl.append((item, "rgb(254,178,76)"))
            elif item < 5/9*40:
                self.wind_gusts_cl.append((item, "rgb(253,141,60)"))
            elif item < 6/9*40:
                self.wind_gusts_cl.append((item, "rgb(252,78,42)"))
            elif item < 7/9*40:
                self.wind_gusts_cl.append((item, "rgb(227,26,28)"))
            elif item < 8/9*40:
                self.wind_gusts_cl.append((item, "rgb(189,0,38)"))
            else:
                self.wind_gusts_cl.append((item, "rgb(128,0,38)"))

        for item in self.wind_speeds_ARO_2:
            if item == "-":
                self.wind_speeds_ARO_2_cl.append((item, "rgb(255,255,255)"))
            elif item < 1/9*40:
                self.wind_speeds_ARO_2_cl.append((item, "rgb(255,255,204)"))
            elif item < 2/9*40:
                self.wind_speeds_ARO_2_cl.append((item, "rgb(255,237,160)"))
            elif item < 3/9*40:
                self.wind_speeds_ARO_2_cl.append((item, "rgb(254,217,118)"))
            elif item < 4/9*40:
                self.wind_speeds_ARO_2_cl.append((item, "rgb(254,178,76)"))
            elif item < 5/9*40:
                self.wind_speeds_ARO_2_cl.append((item, "rgb(253,141,60)"))
            elif item < 6/9*40:
                self.wind_speeds_ARO_2_cl.append((item, "rgb(252,78,42)"))
            elif item < 7/9*40:
                self.wind_speeds_ARO_2_cl.append((item, "rgb(227,26,28)"))
            elif item < 8/9*40:
                self.wind_speeds_ARO_2_cl.append((item, "rgb(189,0,38)"))
            else:
                self.wind_speeds_ARO_2_cl.append((item, "rgb(128,0,38)"))


        a_min = self.off - 60
        a_max = self.off + 60

        self.wind_degs_off = []
        for item in self.wind_degs:
            if a_min < 0:
                if item > 180:
                    item -= 360
            if a_max > 360:
                if item < 180:
                    item += 360
            if a_min < item < a_max:
                self.wind_degs_off.append((item, False))
            else:
                self.wind_degs_off.append((item, True))

        self.spot_score = 0
        i = 0
        for item in self.wind_speeds:
            if self.wind_degs_off[i][1]:
                self.spot_score += item
            i += 1


def get_forecast():
    spot_list = []
    spot_db = Spot.query.all()
    for spot in spot_db:
        spot_list.append(Forecast(spot.name, spot.lat, spot.long, spot.offside))
    sorted_spot_list = sorted(spot_list, key=operator.attrgetter("spot_score"))[::-1]
    return sorted_spot_list


new_spot_list = get_forecast()


@app.route('/')
def home():
    new_spot_list = get_forecast()
    return render_template("index.html", spot_list=new_spot_list)


@app.route('/spot/<int:spot_id>')
def spot(spot_id):
    spot = Spot.query.get(spot_id)
    return render_template("spot.html", spot_list=new_spot_list, spot=spot)


@app.route('/add-spot')
def add_spot():
    return render_template("add_spot.html", spot_list=new_spot_list)


@app.route('/about')
def about():
    return render_template("about.html", spot_list=new_spot_list)


@app.route('/contact')
def contact():
    return render_template("contact.html", spot_list=new_spot_list)


@app.route('/admin')
def admin():
    spots = Spot.query.all()
    return render_template("admin.html", spots=spots)


@app.route("/new-spot", methods=['GET', 'POST'])
def add_new_spot():
    form = SpotForm()
    if form.validate_on_submit():
        new_spot = Spot(
            name=form.name.data,
            lat=form.lat.data,
            long=form.long.data,
            offside=form.offside.data,
        )
        db.session.add(new_spot)
        db.session.commit()
        return redirect(url_for("admin"))
    return render_template("add-edit.html", form=form)


@app.route("/edit-spot/<int:spot_id>", methods=['GET', 'POST'])
def edit_spot(spot_id):
    spot = Spot.query.get(spot_id)
    edit_form = SpotForm(
        name=spot.name,
        lat=spot.lat,
        long=spot.long,
        offside=spot.offside
    )
    if edit_form.validate_on_submit():
        spot.name = edit_form.name.data
        spot.lat = edit_form.lat.data
        spot.long = edit_form.long.data
        spot.offside = edit_form.offside.data
        db.session.commit()
        return redirect(url_for("admin"))
    return render_template("add-edit.html", form=edit_form)


@app.route("/delete/<int:spot_id>")
def delete_spot(spot_id):
    spot_to_delete = Spot.query.get(spot_id)
    db.session.delete(spot_to_delete)
    db.session.commit()
    return redirect(url_for('admin'))


@app.route('/test')
def test():
    return render_template("not_used/buttons.html")



@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html', spot_list=new_spot_list), 404


@app.errorhandler(500)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html', spot_list=new_spot_list), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
