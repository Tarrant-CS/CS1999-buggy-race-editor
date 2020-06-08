from flask import Flask, render_template, request, jsonify
import sqlite3 as sql
app = Flask(__name__)

DATABASE_FILE = "database.db"
DEFAULT_BUGGY_ID = "1"

BUGGY_RACE_SERVER_URL = "http://rhul.buggyrace.net"


#------------------------------------------------------------
# the index page
#------------------------------------------------------------
@app.route('/')
def home():
   return render_template('index.html', server_url=BUGGY_RACE_SERVER_URL)

#------------------------------------------------------------
# creating a new buggy:
#  if it's a POST request process the submitted data
#  but if it's a GET request, just show the form
#------------------------------------------------------------
@app.route('/new', methods = ['POST', 'GET', 'DELETE'])
def create_buggy():
  if request.method == 'GET':

    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies")
    record = cur.fetchone(); 

    return render_template("buggy-form.html", buggy = None)
  
  elif request.method == 'POST':
    msg=""
    violation=""
    qty_wheels = request.form['qty_wheels']
    power_units = request.form['power_units']
    aux_power_units = request.form['aux_power_units']
    qty_tyres = request.form['qty_tyres']
    qty_attacks = request.form['qty_attacks']
    hamster_booster = request.form['hamster_booster']
    if not qty_wheels.isdigit():
      msg = 'This is not a digit, please input a digit'
      return render_template('buggy-form.html', msg = msg)
    if not (int(qty_wheels) % 2 == 0):
      violation = 'RULES VIOLATION: Number of wheels must be even'
    if (int(qty_wheels) < 3):
      violation = 'RULES VIOLATION: Number of wheels must be greater than 3'
    
    try: 
      buggy_id = request.form['id']
      flag_color = request.form['flag_color']
      power_type = request.form['power_type']
      aux_power_type = request.form['aux_power_type']
      flag_pattern = request.form['flag_pattern']
      flag_color_secondary = request.form['flag_color_secondary']
      tyres = request.form['tyres']
      armour = request.form['armour']
      attack = request.form['attack']
      fireproof = request.form['fireproof']
      insulated = request.form['insulated']
      antibiotic = request.form['antibiotic']
      banging = request.form['banging']
      algo = request.form['algo']
      with sql.connect(DATABASE_FILE) as con:
        cur = con.cursor()
        if buggy_id.isdigit():
          cur.execute("UPDATE buggies set qty_wheels=?, flag_color=?, power_type=?, aux_power_type=?, flag_pattern=?, flag_color_secondary=?, tyres=?, armour=?, attack=?, fireproof=?, insulated=?, antibiotic=?, banging=?, algo=?, power_units=?, aux_power_units=?, qty_tyres=?, qty_attacks=?, hamster_booster=? WHERE id=?", (
          qty_wheels, flag_color, power_type, aux_power_type, flag_pattern, flag_color_secondary, tyres, armour, attack, fireproof, insulated, antibiotic, banging, algo, power_units, aux_power_units, qty_tyres, qty_attacks, hamster_booster, buggy_id))
        else:
          cur.execute("INSERT INTO buggies (qty_wheels, flag_color, power_type, aux_power_type, flag_pattern, flag_color_secondary, tyres, armour, attack, fireproof, insulated, antibiotic, banging, algo, power_units, aux_power_units, qty_tyres, qty_attacks, hamster_booster) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (qty_wheels, flag_color, power_type, aux_power_type, flag_pattern, flag_color_secondary, tyres, armour, attack, fireproof, insulated, antibiotic, banging, algo, power_units, aux_power_units, qty_tyres, qty_attacks, hamster_booster,)) 
          con.commit()
        msg = "Record successfully saved"
    except Exception as e:
      con.rollback()
      msg += e
    finally:
      con.close()
      return render_template("updated.html", msg = msg, violation = violation)

  elif request.method == 'DELETE':
    try:
      msg = "deleting buggy"
      with sql.connect(DATABASE_FILE) as con:
        cur = con.cursor()
        cur.execute("DELETE FROM buggies qty_wheels=?, flag_color=?, power_type=?, aux_power_type=?, flag_pattern=?, flag_color_secondary=?, tyres=?, armour=?, attack=?, fireproof=?, insulated=?, antibiotic=?, banging=?, algo=?, power_units=?, aux_power_units=?, qty_tyres=?, qty_attacks=?, hamster_booster=? WHERE id=?", (
          qty_wheels, flag_color, power_type, aux_power_type, flag_pattern, flag_color_secondary, tyres, armour, attack, fireproof, insulated, antibiotic, banging, algo, power_units, aux_power_units, qty_tyres, qty_attacks, hamster_booster, buggy_id,))
 
        con.commit()
        msg = "Buggy deleted"
    except:
      con.rollback()
      msg = "error in delete operation"
    finally:
      con.close()
      return render_template("updated.html", msg = msg)
    

  

#------------------------------------------------------------
# a page for displaying the buggy
#------------------------------------------------------------
@app.route('/buggy')
def show_buggies():
  con = sql.connect(DATABASE_FILE)
  con.row_factory = sql.Row
  cur = con.cursor()
  cur.execute("SELECT * FROM buggies")
  records = cur.fetchall(); 
  return render_template("buggy.html", buggies = records)

#------------------onerecords = cur.fetchone-------------------------------------
# a page for editing onerecords = cur.fetchone buggy
#--------------------onerecords = cur.fetchone-------------------------------------
@app.route('/edit/<buggy_id>')
def edit_buggy(buggy_id):
  con = sql.connect(DATABASE_FILE)
  con.row_factory = sql.Row
  cur = con.cursor()
  cur.execute("SELECT * FROM buggies WHERE id=?", (buggy_id,))
  record = cur.fetchone()
  return render_template("buggy-form.html", buggy = record)


#------------------------------------------------------------
# get JSON from current record
#   this is still probably right, but we won't be
#   using it because we'll be dipping diectly into the
#   database
#------------------------------------------------------------
@app.route('/json')
def summary():
  con = sql.connect(DATABASE_FILE)
  con.row_factory = sql.Row
  cur = con.cursor()
  cur.execute("SELECT * FROM buggies WHERE id=? LIMIT 1", (DEFAULT_BUGGY_ID))
  return jsonify(
      {k: v for k, v in dict(zip(
        [column[0] for column in cur.description], cur.fetchone())).items()
        if (v != "" and v is not None)
      }
    )

#------------------------------------------------------------
# delete the buggy
#   don't want DELETE here, because we're anticipating
#   there always being a record to update (because the
#   student needs to change that!)
#------------------------------------------------------------
@app.route('/delete/<buggy_id>')
def delete_buggy(buggy_id):
  try:
    msg = "deleting buggy"
    with sql.connect(DATABASE_FILE) as con:
      cur = con.cursor()
      cur.execute("DELETE FROM buggies WHERE id=?", (buggy_id,))
      con.commit()
      msg = "Buggy deleted"
  except:
    con.rollback()
    msg = "error in delete operation"
  finally:
    con.close()
    return render_template("updated.html", msg = msg)


if __name__ == '__main__':
   app.run(debug = True, host="0.0.0.0")
