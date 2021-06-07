from flask import Flask, render_template, request, jsonify
import sqlite3 as sql
import os


tyre_dict = {
"knobbly" : 15,
"slick" : 10,
"steelband" : 20,
"reactive" : 40,
"maglev" : 50
}

power_dict = {
    "petrol" : 4,
    "fusion" : 400,
    "steam" : 3,
    "bio" : 5,
    "electric" : 20,
    "rocket" : 16,
    "hamster" : 3,
    "thermo" : 300,
    "solar" : 40,
    "wind" : 20
}

non_consumables = ["fusion", "thermo", "solar", "wind"]

# app - The flask application where all the magical things are configured.
app = Flask(__name__)

# Constants - Stuff that we need to know that won't ever change!
DATABASE_FILE = "database.db"
DEFAULT_BUGGY_ID = "1"
BUGGY_RACE_SERVER_URL = "http://rhul.buggyrace.net"

#------------------------------------------------------------
# the index page
#------------------------------------------------------------
@app.route('/')
def home():
    return render_template('initial.html', server_url=BUGGY_RACE_SERVER_URL)

#------------------------------------------------------------
# creating a new buggy:
#  if it's a POST request process the submitted data
#  but if it's a GET request, just show the form
#------------------------------------------------------------
def return_values():
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies")
    record = cur.fetchone(); 
    return record



@app.route('/new', methods = ['POST', 'GET'])
def create_buggy():
    if request.method == 'GET':
        record = return_values()
        return render_template("buggy-form.html", buggy = record)
    elif request.method == 'POST':
        msg=""
        qty_wheels = int(request.form['qty_wheels'])
        flag_color = request.form['flag_color']
        flag_color_secondary = request.form['flag_color_secondary']
        flag_pattern = request.form['flag_pattern']
        power_type = request.form['power_type'] 
        tyres =  request.form['tyres']
        qty_tyres =  int(request.form['qty_tyres'])     
        power_units = int(request.form['power_units'])
        aux_power_type = request.form['aux_power_type']
        aux_power_units = int(request.form['aux_power_units'])
        cost = 0

     
        

        if qty_wheels %2 != 0  or qty_wheels<4 :    
            msg = "You must enter an even number for amount of wheels:"
            record = return_values()
            return render_template("buggy-form.html", msg=msg, buggy = record)

        if qty_tyres < qty_wheels:
            msg = "Amount of tyres must be more than amount of quantity of wheels."
            record = return_values()
            return render_template("buggy-form.html", msg=msg, buggy = record)

        if flag_color== flag_color_secondary and flag_pattern != "plain":
            msg = "You cant have two of the same colors if you have a pattern other than plain."
            record = return_values()
            return render_template("buggy-form.html", msg=msg, buggy = record)
        
        if flag_color!= flag_color_secondary and flag_pattern == "plain":
            msg = "You cant have two different if your pattern is plain."
            record = return_values()
            return render_template("buggy-form.html", msg=msg, buggy = record)


        if  power_type in non_consumables and  power_units >1 :
            msg = f"You can't have more than 1 power_unit for this {power_type}."
            record = return_values()
            return render_template("buggy-form.html", msg=msg, buggy = record)

        if  aux_power_type in non_consumables and  aux_power_units >1 :
            msg = f"You can't have more than 1 aux_power_unit for {aux_power_type}"
            record = return_values()
            return render_template("buggy-form.html", msg=msg, buggy = record)      
  
    
        for i in tyre_dict:
            if tyres == i:
                cost += (tyre_dict[i] * qty_tyres)

        for i in power_dict:
            if power_type == i:
                cost += (power_dict[i] * power_units)
        
        
        for i in power_dict:
            if aux_power_type == i:
                cost += (power_dict[i] * aux_power_units)


        cost_message = cost



        try:
            with sql.connect(DATABASE_FILE) as con: 
                cur = con.cursor()
                cur.execute(
                    """UPDATE buggies set qty_wheels=?, flag_color=?, flag_color_secondary=?, flag_pattern=?, power_type=?, tyres=?, qty_tyres=?, 
                    power_units=?, aux_power_type=?, aux_power_units=?, cost=? WHERE id=?""",
                    (qty_wheels,flag_color,flag_color_secondary,flag_pattern,power_type,tyres,qty_tyres,power_units,aux_power_type,aux_power_units,cost,
                     DEFAULT_BUGGY_ID)	
                    )
               
           
                
                con.commit()
                msg = "Record successfully saved"

        except:
            con.rollback()
            msg = "error in update operation"
        finally:
            con.close()
        return render_template("updated.html", msg = msg, cost_message = cost_message)

#------------------------------------------------------------
# a page for displaying the buggy
#------------------------------------------------------------
@app.route('/buggy')
def show_buggies():
    record = return_values()
    return render_template("buggy.html", buggy = record)

#------------------------------------------------------------
# a placeholder page for editing the buggy: yo`u'll need
# to change this when you tackle task 2-EDIT
#------------------------------------------------------------
@app.route('/edit')
def edit_buggy():
    return render_template("buggy-form.html")
	
@app.route('/posters')
def poster_add():
	return render_template("poster.html")
	


#------------------------------------------------------------
# You probably don't need to edit this... unless you want to ;)
#
# get JSON from current record
#  This reads the buggy record from the database, turns it
#  into JSON format (excluding any empty values), and returns
#  it. There's no .html template here because it's *only* returning
#  the data, so in effect jsonify() is rendering the data.
#------------------------------------------------------------
@app.route('/json')
def summary():
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies WHERE id=? LIMIT 1", (DEFAULT_BUGGY_ID))

    buggies = dict(zip([column[0] for column in cur.description], cur.fetchone())).items() 
    return jsonify({ key: val for key, val in buggies if (val != "" and val is not None) })







# You shouldn't need to add anything below this!
if __name__ == '__main__':
    app.run(debug = True, host="0.0.0.0")
