import mysql.connector
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin


my_host="db-mysql"
my_user="root"
my_password="testpassword"
my_database="french"

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['JSON_AS_ASCII'] = False


total_learning = 20
total_learning_to_show = 5
total_known_to_show = 1
total_correct_needed = 10

def my_db():
    return mysql.connector.connect(
        host=my_host,
        user=my_user,
        password=my_password,
        database=my_database,
        charset = 'utf8'
    )


@app.route('/phrases/repopulate', methods=['GET'])
@cross_origin()
def repopulate_phrases():
    mydb = my_db()
    mycursor = mydb.cursor(dictionary=True)

    mycursor.execute("""
    SELECT count(*) as 'count' FROM phrases where status='Learning';
    """)

    learning_count = mycursor.fetchone()

    response = 'Not Needed'

    if learning_count['count'] < total_learning:
        how_many_more_needed = total_learning - learning_count['count']
        mycursor.execute("""
        UPDATE phrases SET status = 'Learning' where status = 'Todo' order by RAND() LIMIT %s
        """, [how_many_more_needed])
        mydb.commit()

        if mycursor.rowcount == how_many_more_needed:
            response =  f'repopulated {how_many_more_needed}'
        else:
            response = f'Needed to repopulate {how_many_more_needed}, but only repopulated {mycursor.rowcount} due to insufficient Todo phrases.'

    mycursor.close()
    mydb.close()
    return response

@app.route('/phrases', methods=['GET'])
@cross_origin()
def get_phrases():
    mydb = my_db()
    mycursor = mydb.cursor(dictionary=True)

    mycursor.execute("""
    (SELECT * FROM phrases where status='Learning' ORDER BY RAND() limit %s)
    UNION
    (SELECT * FROM phrases where status='Known' ORDER BY RAND() limit %s);
    """, (total_learning_to_show, total_known_to_show))

    myresult = mycursor.fetchall()

    mycursor.close()
    mydb.close()
    return jsonify(myresult)

@app.route('/phrases/all', methods=['GET'])
@cross_origin()
def get_all_phrases():
    mydb = my_db()
    mycursor = mydb.cursor(dictionary=True)

    mycursor.execute("""
    SELECT * FROM phrases;
    """)

    myresult = mycursor.fetchall()

    mycursor.close()
    mydb.close()
    return jsonify(myresult)

@app.route('/phrase_attempt/<phrase_id>/<correct>', methods=['POST'])
@cross_origin()
def phrase_attempt(phrase_id, correct):
    now = datetime.now()

    mydb = my_db()
    mycursor = mydb.cursor(dictionary=True)

    is_correct = correct == 'true'

    mycursor.execute("INSERT INTO phrase_attempts (phrase_id, correct, created_on) VALUES (%s, %s, %s)",
    (phrase_id, is_correct, now))

    mydb.commit()

    correct_to_go = total_correct_needed

    if is_correct == False:
        mycursor.execute("UPDATE phrases SET status = 'Learning' where id = %s and status = 'Known'", [phrase_id])
        if mycursor.rowcount > 0:
            mydb.commit()
            mycursor.close()
            mydb.close()
            return '{"status": "Unlearned"}'

    if is_correct == True:
        mycursor.execute(f"""
        SELECT id FROM phrase_attempts where
        phrase_id=%s and
        created_on > (SELECT created_on from
            ((select MAX(created_on) as 'created_on' from phrase_attempts where phrase_id=%s and correct=False)
                UNION
            (select MIN(created_on) as 'created_on' from phrase_attempts where phrase_id=%s and correct=True)) as thing
            where created_on is not null
            LIMIT 1);
        """, [phrase_id,phrase_id,phrase_id])
        myresult = mycursor.fetchall()
        correct_to_go = total_correct_needed - (len(myresult)+1)

        if correct_to_go <= 0:
            mycursor.execute("UPDATE phrases SET status = 'Known' where id = %s and status = 'Learning'", [phrase_id])
            mydb.commit()
            if mycursor.rowcount > 0:
                mycursor.close()
                mydb.close()
                return '{"status": "Learned"}'


    mycursor.execute("""
    SELECT status FROM phrases where id = %s;
    """, [phrase_id])

    myresult = mycursor.fetchone()
    if myresult['status'] == 'Learning':
        myresult['togo'] = correct_to_go

    mycursor.close()
    mydb.close()
    return jsonify(myresult)

@app.route('/phrase_attempts/<phrase_id>', methods=['GET'])
@cross_origin()
def get_phrase_attempts(phrase_id):
    mydb = my_db()
    mycursor = mydb.cursor(dictionary=True)

    mycursor.execute("""
    (SELECT correct, created_on FROM phrase_attempts where phrase_id=%s ORDER BY created_on DESC);
    """, [phrase_id])

    myresult = mycursor.fetchall()

    mycursor.close()
    mydb.close()
    return jsonify(myresult)

@app.route('/phrase/<phrase_id>', methods=['GET'])
@cross_origin()
def get_phrase(phrase_id):
    mydb = my_db()
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

    mycursor.close()
    mydb.close()
    return jsonify(phrase)

@app.route('/phrase', methods=['POST'])
def phrase():

    content_type = request.headers.get('Content-Type')

    if (content_type != 'application/json'):

        return 'Content-Type not supported!'

    json = request.json


    mydb = my_db()
    mycursor = mydb.cursor(dictionary=True)

    mycursor.execute("INSERT INTO phrases (english, french, status) VALUES (%s, %s, %s)",
    (json['english'], json['french'], 'Todo'))

    mydb.commit()

    mycursor.close()
    mydb.close()
    return 'success'

@app.route('/phrase/<phrase_id>/<status>', methods=['PUT'])
def phrase_status_update(phrase_id, status):

    mydb = my_db()
    mycursor = mydb.cursor(dictionary=True)

    mycursor.execute("UPDATE phrases SET status = %s where id = %s",
    (status, phrase_id))

    mydb.commit()
    mycursor.close()
    mydb.close()

    return 'success'


if __name__ == '__main__':
    app.run()