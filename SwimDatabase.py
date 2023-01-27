# %% [markdown]
# 
# swimmers:
# 
#     unique id
#     name 
#     age 
# 
# 
# strokes:
# 
#     unique id 
#     distance 
#     stroke 
# 
# 
# times:
# 
#     swimmer_id
#     stroke_id
#     time 
#     timestamp
# 
# 
# create database swimdataDB;
# 
# grant all on swimdataDB.* to 'swimuser'@'localhost' identified by 'swimpasswd';
# 
# create table swimmers (
#     id int not null auto_increment primary key,
#     name varchar(32) not null,
#     age int not null
# );
# 
# create table strokes (
#     id int not null auto_increment primary key,
#     distance varchar(16) not null,
#     stroke varchar(16) not null
# );
# 
# create table times (
#     swimmer_id int not null,
#     stroke_id int not null,
#     time varchar(16) not null,
#     ts timestamp default current_timestamp
# );
# 
# ----------------------------------------------------------------------
# 
# MariaDB [swimdataDB]> describe strokes;
# +----------+-------------+------+-----+---------+----------------+
# | Field    | Type        | Null | Key | Default | Extra          |
# +----------+-------------+------+-----+---------+----------------+
# | id       | int(11)     | NO   | PRI | NULL    | auto_increment |
# | distance | varchar(16) | NO   |     | NULL    |                |
# | stroke   | varchar(16) | NO   |     | NULL    |                |
# +----------+-------------+------+-----+---------+----------------+
# 
# 
# MariaDB [swimdataDB]> describe swimmers;
# +-------+-------------+------+-----+---------+----------------+
# | Field | Type        | Null | Key | Default | Extra          |
# +-------+-------------+------+-----+---------+----------------+
# | id    | int(11)     | NO   | PRI | NULL    | auto_increment |
# | name  | varchar(32) | NO   |     | NULL    |                |
# | age   | int(11)     | NO   |     | NULL    |                |
# +-------+-------------+------+-----+---------+----------------+
# 
# 
# MariaDB [swimdataDB]> describe times;
# +------------+-------------+------+-----+---------------------+-------+
# | Field      | Type        | Null | Key | Default             | Extra |
# +------------+-------------+------+-----+---------------------+-------+
# | swimmer_id | int(11)     | NO   |     | NULL                |       |
# | stroke_id  | int(11)     | NO   |     | NULL                |       |
# | time       | varchar(16) | NO   |     | NULL                |       |
# | ts         | timestamp   | YES  |     | current_timestamp() |       |
# +------------+-------------+------+-----+---------------------+-------+
# 

# %%
import os

FOLDER = "swimdata/"

files = os.listdir(FOLDER)

files.remove(".DS_Store")

# %%
len(files)

# %%
print(files)

# %%
import DBcm

# %%
from appconfig import config


# %%
with DBcm.UseDatabase(config) as db:
    name = "Abi"
    age = 9
    SQL = "select * from swimmers where name = %s and age = %s;"  # %s is a placeholder.
    db.execute(SQL, (name, age))
    results = db.fetchall()

# %%
results

# %%
def insert_if_not_already_there(connection, table, field1, field2, value1, value2):
    SQL = f"select * from {table} where {field1} = %s and {field2} = %s;"
    connection.execute(SQL, (value1, value2))
    results = connection.fetchall()
    if results:
        pass
    else:
        SQL = f"insert into {table} ({field1}, {field2}) values (%s, %s)"
        db.execute(SQL, (value1, value2))

# %%
with DBcm.UseDatabase(config) as db:
    for fn in files:
        name, age, distance, stroke = fn.removesuffix(".txt").split("-")
        insert_if_not_already_there(db, "swimmers", "name", "age", name, age)
        insert_if_not_already_there(
            db, "strokes", "distance", "stroke", distance, stroke
        )

# %%
with DBcm.UseDatabase(config) as db:
    SQL = "select id from swimmers where name = 'Darius' and age = 13"
    db.execute(SQL)
    results = db.fetchone()[0]
results

# %%
def get_id(connection, table, field1, field2, value1, value2):
    SQL = f"select id from {table} where {field1} = %s and {field2} = %s"
    connection.execute(SQL, (value1, value2))
    return connection.fetchone()[0]

# %%
import swimclub

with DBcm.UseDatabase(config) as db:
    for fn in files:
        *_, times, _ = swimclub.get_swim_data(fn)
        name, age, distance, stroke = fn.removesuffix(".txt").split("-")
        swimmer_id = get_id(db, "swimmers", "name", "age", name, age)
        stroke_id = get_id(db, "strokes", "distance", "stroke", distance, stroke)
        for t in times:
            SQL = "insert into times (swimmer_id, stroke_id, time) values (%s, %s, %s)"
            db.execute(SQL, (swimmer_id, stroke_id, t))

# %% [markdown]
# ##### At this point, the data is in the database tables, so we can work with it (as opposed to going back to the filesystem).

# %%
import DBcm
from appconfig import config

swimmer_name = "Katie"
swimmer_age = 9

event_distance = "100m"
event_stroke = "Back"

SQL = """
        select swimmers.name, swimmers.age, times.time, strokes.distance, strokes.stroke, times.ts
        from swimmers, times, strokes
        where (swimmers.name = %s and swimmers.age = %s) and
        (strokes.distance = %s and strokes.stroke = %s) and
        swimmers.id = times.swimmer_id and
        strokes.id = times.stroke_id
"""

with DBcm.UseDatabase(config) as db:
    db.execute(
        SQL,
        (
            swimmer_name,
            swimmer_age,
            event_distance,
            event_stroke,
        ),
    )
    results = db.fetchall()


# %%
for row in results:
    print(row)

# %%
import DBcm

from appconfig import config


def get_swimmers_data(name, age, distance, stroke):
    SQL = """
        select swimmers.name, swimmers.age, times.time, strokes.distance, strokes.stroke, times.ts
        from swimmers, times, strokes
        where (swimmers.name = %s and swimmers.age = %s) and
        (strokes.distance = %s and strokes.stroke = %s) and
        swimmers.id = times.swimmer_id and
        strokes.id = times.stroke_id
    """
    with DBcm.UseDatabase(config) as db:
        db.execute(
            SQL,
            (
                name,
                age,
                distance,
                stroke,
            ),
        )
        results = db.fetchall()
    return results


# %%
for row in get_swimmers_data("Darius", 13, "200m", "IM"):
    print(row)

# %%
for row in get_swimmers_data("Chris", 17, "100m", "Back"):
    print(row)

# %%
# List a named swimmer's events (as stored in the database).

import DBcm

from appconfig import config

swimmer = "Hannah"

SQL = """ 
    select distinct strokes.distance, strokes.stroke
    from swimmers, strokes, times
    where times.swimmer_id = swimmers.id and
    times.stroke_id = strokes.id and
    swimmers.name = %s;
"""

with DBcm.UseDatabase(config) as db:
    db.execute(SQL, (swimmer,))
    results = db.fetchall()
results
## list(set(results))


# %%
events = [t[0] + "-" + t[1] for t in results]
events

# %%
SQL = "select name from swimmers"
with DBcm.UseDatabase(config) as db:
    db.execute(SQL)
    results = db.fetchall()

# %%
results

# %%
names = [t[0] for t in results]  # 't' is the current tuple.

# %%
print(sorted(names))

# %%


# %%
import data_utils

# %%
data_utils.get_list_of_sessions()

# %%
sessions = data_utils.get_list_of_sessions()

# %%
sessions

# %%
sessions[0][0]

# %%
print(dir(sessions[0][0]))

# %%
sessions[0][0].ctime()

# %%
sessions[0][0].isoformat()

# %%
sessions[0][0].isoformat().split("T")[0]

# %%
sessions[0][0].isoformat().split("T")[1]

# %%
for row in sessions:
    print(row[0].isoformat().split("T")[0])

# %%
SQL = """select * from times where date_format(ts, "%Y-%m-%d") = "2022-12-08";"""

# %%
sessions = [
    row[0].isoformat().split("T")[0] for row in data_utils.get_list_of_sessions()
]

# %%
sessions

# %%
sorted(sessions, reverse=True)

# %%
sorted(["2022-12-08", "2022-12-01", "2026-01-01"], reverse=True)

# %%
SQL = """
    select distinct swimmers.name   
    from times, swimmers 
    where date_format(times.ts, "%Y-%m-%d") = %s and     
    times.swimmer_id = swimmers.id 
    order by name
"""

# %%
with DBcm.UseDatabase(config) as db:
    db.execute(SQL, (sessions[0],))
    results = db.fetchall()
[row[0] for row in results]

# %%



