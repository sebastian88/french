import mysql.connector
from datetime import datetime
from flask import Flask, jsonify, Response, request
from flask_cors import CORS, cross_origin


mydb = mysql.connector.connect(
  host="db-mysql",
  user="root",
  password="testpassword",
  database="french",
  charset = 'utf8'
)

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['JSON_AS_ASCII'] = False


total_learning = 20
total_learning_to_show = 5
total_known_to_show = 1

@app.route('/phrases/repopulate', methods=['GET'])
@cross_origin()
def repopulate_phrases():
    mycursor = mydb.cursor(dictionary=True)

    mycursor.execute("""
    SELECT count(*) as 'count' FROM phrases where status='Learning';
    """)

    learning_count = mycursor.fetchone()
    
    if learning_count['count'] < total_learning:
        how_many_more_needed = total_learning - learning_count['count']
        mycursor.execute("""
        UPDATE phrases SET status = 'Learning' where status = 'Todo' order by RAND() LIMIT %s
        """, [how_many_more_needed])

        if mycursor.rowcount == how_many_more_needed:
            return f'repopulated {how_many_more_needed}'
        else:
            print(mycursor.rowcount)
            return f'Needed to repopulate {how_many_more_needed}, but only repopulated {mycursor.rowcount} due to insufficient Todo phrases.'

    return 'Not needed'

@app.route('/phrases', methods=['GET'])
@cross_origin()
def get_phrases():
    mycursor = mydb.cursor(dictionary=True)

    mycursor.execute("""
    (SELECT * FROM phrases where status='Learning' ORDER BY RAND() limit %s) 
    UNION 
    (SELECT * FROM phrases where status='Known' ORDER BY RAND() limit %s);
    """, (total_learning_to_show, total_known_to_show))

    myresult = mycursor.fetchall()

    return myresult

@app.route('/phrases/all', methods=['GET'])
@cross_origin()
def get_all_phrases():
    mycursor = mydb.cursor(dictionary=True)

    mycursor.execute("""
    SELECT * FROM phrases;
    """)

    myresult = mycursor.fetchall()

    return myresult
    
@app.route('/phrase_attempt/<phrase_id>/<correct>', methods=['POST'])
@cross_origin()
def phrase_attempt(phrase_id, correct):
    now = datetime.now()

    mycursor = mydb.cursor(dictionary=True)

    is_correct = correct == 'true'

    mycursor.execute("INSERT INTO phrase_attempts (phrase_id, correct, created_on) VALUES (%s, %s, %s)", 
    (phrase_id, is_correct, now))

    mydb.commit()

    # Check if it has been learned and if new questions need to be added in. 

    correct_to_go = 10

    if is_correct == False:
        mycursor.execute("UPDATE phrases SET status = 'Learning' where id = %s and status = 'Known'", [phrase_id])
        if mycursor.rowcount > 0:
            return '{"status": "Unlearned"}'

    if is_correct == True:
        mycursor.execute(f"""
        SELECT id FROM phrase_attempts where 
        phrase_id=%s and 
        created_on > (SELECT * from 
            ((select MAX(created_on) from phrase_attempts where phrase_id=%s and correct=False)
                UNION
            (select MIN(created_on) from phrase_attempts where phrase_id=%s and correct=True)) as thing
            LIMIT 1);
        """, [phrase_id,phrase_id,phrase_id])
        myresult = mycursor.fetchall()
        correct_to_go = 10 - len(myresult)

        if len(myresult) >= 10:
            mycursor.execute("UPDATE phrases SET status = 'Known' where id = %s and status = 'Learning'", [phrase_id])
            if mycursor.rowcount > 0:
                return '{"status": "Learned"}'


    mycursor.execute("""
    SELECT status FROM phrases where id = %s;
    """, [phrase_id])

    myresult = mycursor.fetchone()
    if myresult['status'] == 'Learning':
        myresult['togo'] = correct_to_go
    return myresult

@app.route('/phrase_attempts/<phrase_id>', methods=['GET'])
@cross_origin()
def get_phrase_attempts(phrase_id):
    mycursor = mydb.cursor(dictionary=True)

    mycursor.execute("""
    (SELECT correct, created_on FROM phrase_attempts where phrase_id=%s ORDER BY created_on DESC);
    """, [phrase_id])

    myresult = mycursor.fetchall()

    return myresult

@app.route('/phrase/<phrase_id>', methods=['GET'])
@cross_origin()
def get_phrase(phrase_id):
    mycursor = mydb.cursor(dictionary=True)

    mycursor.execute("""
    SELECT * FROM phrases where id=%s;
    """, [phrase_id])

    phrase = mycursor.fetchone()

    mycursor.execute("""
    (SELECT correct, created_on FROM phrase_attempts where phrase_id=%s ORDER BY created_on DESC);
    """, [phrase_id])

    phrase_attempts = mycursor.fetchall()

    phrase['zattempts'] = phrase_attempts

    return phrase
    
@app.route('/phrase', methods=['POST'])
def phrase():
    
    content_type = request.headers.get('Content-Type')
    
    if (content_type != 'application/json'):
        
        return 'Content-Type not supported!'

    json = request.json
    

    mycursor = mydb.cursor(dictionary=True)

    mycursor.execute("INSERT INTO phrases (english, french, status) VALUES (%s, %s, %s)", 
    (json['english'], json['french'], 'Todo'))

    mydb.commit()

    return 'success'
    
@app.route('/phrase/<phrase_id>/<status>', methods=['PUT'])
def phrase_status_update(phrase_id, status):
    
    mycursor = mydb.cursor(dictionary=True)

    mycursor.execute("UPDATE phrases SET status = %s where id = %s", 
    (status, phrase_id))

    mydb.commit()

    return 'success'


if __name__ == '__main__':
    app.run()