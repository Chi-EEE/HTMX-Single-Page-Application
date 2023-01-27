from flask import Flask, session, render_template, request, Response

import data_utils


app = Flask(__name__)  # Creates a web server which can run your Flask code.and
app.secret_key = (
    "kjhfdskjhfsdghk;odgkjsdkjsdkgsdgjdsghdjgdghdfghdfgdfghfggdf;uaghdfgagf"
)
app.config["SESSION_TYPE"] = "filessystem"


@app.get("/")  # The @ symbol is a Python decorator.
def homepage():
    session_dates = [
        row[0].isoformat().split("T")[0] for row in data_utils.get_list_of_sessions()
    ]
    return render_template(
        "index.html",
        title="Welcome to Swimclub",
        sessions=session_dates,
    )


@app.get("/swimmers")
def get_swimmers():
    swim_session = request.args.get("session")
    session["swim_session"] = swim_session  # Let's remember this value.
    names = data_utils.get_swimmers_list_by_session(swim_session)
    response = Response()
    response.headers["HX-Trigger"] = "changedSession"
    response.data = render_template(
        "select.html",
        data=names,
    )
    return response


@app.get("/events")
def get_events():
    swimmer = request.args.get("swimmer")
    session["swimmer"] = swimmer
    data = data_utils.get_swimmer_data(
        swimmer, session["swim_session"]
    )  # A list of three-tuples.
    ages = list(set([t[-1] for t in data]))  # A list of unique ages.
    session["age"] = ages[0]  # The first age from the unique list.
    events = [t[0] + "-" + t[1] for t in data]  # A list of events.
    return render_template(
        "select.html",
        data=events,
    )


def convert2range(v, f_min, f_max, t_min, t_max):
    """Given a value (v) in the range f_min-f_max, convert the value
    to its equivalent value in the range t_min-t_max.

    Based on the technique described here:
        http://james-ramsden.com/map-a-value-from-one-number-scale-to-another-formula-and-c-code/
    """
    return round(t_min + (t_max - t_min) * ((v - f_min) / (f_max - f_min)), 2)


conversion = {
    "Fly": "butterfly",
    "Back": "backstroke",
    "Breast": "breaststroke",
    "Free": "freestyle",
    "IM": "individual medley",
}


@app.get("/get_chart")
def show_event_chart():
    event = request.args.get("event")
    distance, stroke = event.split("-")
    the_stroke = conversion[stroke]
    the_event = f"{distance} {the_stroke}"

    lcmen, lcwomen, scmen, scwomen = data_utils.get_world_records(the_event)

    swim_session = session["swim_session"]

    swimmer = session["swimmer"]
    age = session["age"]
    average_str, times, converts = data_utils.get_chart_data(
        swimmer, age, event, swim_session
    )
    the_converts = [convert2range(c, 0, max(converts), 0, 350) for c in converts]
    chart_data = list(zip(times, the_converts))

    the_title = f"{swimmer} (Under {age}) {event} - {swim_session}"

    return render_template(
        "chart.html",
        title=the_title,
        data=chart_data,
        average=average_str,
        worlds=[lcmen, lcwomen, scmen, scwomen],
    )


if __name__ == "__main__":
    app.run(debug=True)  # Starts the web server, and keeps going...
