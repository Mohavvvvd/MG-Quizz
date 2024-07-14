from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from datetime import date,datetime
app = Flask(__name__)
app.secret_key = 'secret_key'

# Connect to MongoDB
client = MongoClient('mongodb+srv://mohavvvvd:9tC552WfPe8gZsA1@cluster0.gpj3fqg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['Quizz']
users_collection = db['users']
quiz_collection = db["Aquiz"]  
solved_q = db['solve']
today = date.today()
today_str = today.strftime("%Y-%m-%d")
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = users_collection.find_one({'username': username})

    if user and check_password_hash(user['password'], password):
        session['username'] = username
        return redirect(url_for('dashboard'))
    else:
        error = 'Invalid username or password. Please try again.'
        return render_template('index.html', error=error)

@app.route('/signup', methods=['POST'])
def signup():
    new_username = request.form['new_username']
    new_password = request.form['new_password']

    existing_user = users_collection.find_one({'username': new_username})
    if existing_user:
        signup_error = 'Username already exists. Please choose a different one.'
        return render_template('index.html', signup_error=signup_error)

    hashed_password = generate_password_hash(new_password)
    users_collection.insert_one({'username': new_username, 'password': hashed_password})
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    else:
        return redirect(url_for('index'))

@app.route('/welcome')
def welcome():
    if 'username' in session:
        return render_template('welcome.html', username=session['username'])
    else:
        return redirect(url_for('index'))

@app.route('/performance')
def performance():
    if 'username' in session:
        res = list(solved_q.find({'user':session['username']}))
        this_week = 0
        this_month = 0
        general_rating = 0
        all_quizzes_solved = len(res)
        
        for result in res:
            if 'date' in result:
                date_obj = datetime.strptime(result['date'], '%Y-%m-%d').date()
                if (date.today() - date_obj).days <= 7:
                    this_week += 1
                if (date.today() - date_obj).days <= 30:
                    this_month += 1
                general_rating += result['moy']
            else:
                print(f"Document {result} is missing the 'date' field")
        print(general_rating)
        result = list(quiz_collection.find({'user':session['username']}))
        r = list(solved_q.find({'user':session['username']}))
        if len(res)!=0:
            general_rating_avg = general_rating / len(res)
        else:
            general_rating_avg = 0
        return render_template('performance.html', 
                               username=session['username'], 
                               results=result, 
                               resul = r,
                               this_week=this_week, 
                               this_month=this_month, 
                               general_rating=general_rating_avg, 
                               all_quizzes_solved=all_quizzes_solved)
    else:
        return redirect(url_for('index'))
@app.route('/solve')
def quiz():
    if 'username' in session:
        res = list(quiz_collection.find())
        return render_template('solve.html', results = res)
    else:
        return redirect(url_for('index'))

@app.route('/quiz')
def add():
    if 'username' in session:
        return render_template('quiz.html', username=session['username'])
    else:
        return redirect(url_for('index'))

@app.route('/acc_info')
def acc_info():
    if 'username' in session:
        return render_template('acc_info.html', username=session['username'])
    else:
        return redirect(url_for('index'))
@app.route('/add_question', methods=['POST'])
def create_questions():
    try:
        data = request.get_json()
        quiz_collection.insert_one({'user': session['username'], 'title': data[0]['title'], 'description': data[0]['description'], 'level': data[0]['level'], 'questions': data[1:] , 'date':today_str})
        return jsonify({'message': 'Question created successfully'}), 201  
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/up_pass', methods=['POST'])
def up_pass():
    oldp = request.form['op']
    np = request.form['np']
    succ = ""
    error = ""
    existing_user = users_collection.find_one({'username': session['username']}, {'password': 1})
    if existing_user:
        if check_password_hash(existing_user['password'], oldp):
            users_collection.update_one({'username': session['username']}, {'$set': {'password': generate_password_hash(np)}})
            succ = "update with success !"
            return render_template('acc_info.html', succ=succ,username=session['username'])
        else:
            error = "there is an occurred error !"
            return render_template('acc_info.html', error=error,username=session['username'])
        
@app.route('/up_name', methods=['POST'])
def up_name():
    nuser = request.form['user']
    pasw = request.form['pass']
    success = ""
    error = ""
    existing_user = users_collection.find_one({'username': session['username']}, {'password': 1})
    if existing_user:
        if check_password_hash(existing_user['password'], pasw):
            users_collection.update_one({'username': session['username']}, {'$set': {'username': nuser}})
            quiz_collection.update_many({'user': session['username']}, {'$set': {'user': nuser}})
            solved_q.update_many({'user': session['username']}, {'$set': {'user': nuser}})
            success = "update with success !"
            session['username'] = nuser
            return render_template('acc_info.html', username=session['username'], success=success)
        else:
            error = "there is an occurred error !"
            return render_template('acc_info.html', username=session['username'], error=error)
    else:
        error = "user not found !"
        return render_template('acc_info.html', username=session['username'], error=error)
        
@app.route('/search', methods=['POST'])
def search():
    if 'username' in session:
        username = request.form.get('username')
        level = request.form.get('level')
        order = request.form.get('order')  
        if order:
            order = int(order)
        else:
            order = 1  
        query = {}
        if username : 
            query = {'user': username}
        
        if level:
            query['level'] = level
        
        results = list(quiz_collection.find(query).sort('title', order))
        if order == 1 :
            orde = "ASC"
        elif order == -1 :
            orde = "DESC"
        else :
            orde = "None"
        return render_template('solve.html', results=results, username=username , level = level , orde = orde , msg = None)
    else:
        return redirect(url_for('solve'))
    
@app.route('/quizzi', methods=['POST'])
def solve_quiz():
    if 'id' in request.form:
        flask_id = request.form['id']
        print(flask_id)
        id = ObjectId(flask_id)
        print(id)
        query = quiz_collection.find({'_id': id})
        documents = list(query) 
        query.close()  
        print(documents)
        return render_template('qs.html', res=documents,id=id)
    else:
        return 'No id posted', 400
    
@app.route('/test', methods=['POST'])
def test():
    quiz_id = request.form.get('quiz_id')
    try:
        quiz_id = ObjectId(quiz_id)
    except ValueError:
        return "Invalid quiz_id", 400
    quiz_data = quiz_collection.find_one({"_id": quiz_id})
    x = len(quiz_data['questions'])
    if quiz_data:
        answers = request.form
        score = 0
        for i, question in enumerate(quiz_data['questions']):
            user_answer = int(answers.get(f"question_{i}"))
            correct_index = int(question['correctAnswer'])
            if user_answer == correct_index:
                score += 1
        q = solved_q.find_one({'_id':quiz_id,'user':session['username']})
        
        moy = (100 /x ) * score
        if q :
            solved_q.update_one({'_id': quiz_id, 'user': session['username']}, {'$set': {'score': score, 'date': today_str, 'moy': moy}, '$inc': {'num': 1}})
        else:
            solved_q.insert_one({'_id':quiz_id,'user':session['username'],'score':score,'name':answers.get('name'),'num':1,'description':answers.get('dis'),'level':answers.get('lev'),'date':today_str,'moy':moy})
        msg = f"Your score is {score} out of {len(quiz_data['questions'])}!"
        res = list(quiz_collection.find())
        return render_template('solve.html', msg=msg,username = None,orde = None , level = None , results = res)
    else:
        return "Quiz not found", 404

@app.route('/delete', methods=['POST'])
def delete():
    quiz_id = request.form.get('id')
    try:
        quiz_id = ObjectId(quiz_id)
    except ValueError:
        return "Invalid quiz_id", 400
    quiz_data = quiz_collection.find_one({"_id": quiz_id})
    if quiz_data:
        quiz_collection.delete_one({'_id': quiz_id})
        solved_q.delete_one({'name': quiz_data['title']})
        if 'username' in session:
            res = list(solved_q.find({'user': session['username']}))
            this_week = 0
            this_month = 0
            general_rating = 0
            all_quizzes_solved = len(res)
            
            for result in res:
                if 'date' in result:
                    date_obj = datetime.strptime(result['date'], '%Y-%m-%d').date()
                    if (date.today() - date_obj).days <= 7:
                        this_week += 1
                    if (date.today() - date_obj).days <= 30:
                        this_month += 1
                    general_rating += result['moy']
                else:
                    print(f"Document {result} is missing the 'date' field")
            print(general_rating)
            result = list(quiz_collection.find({'user': session['username']}))
            r = list(solved_q.find({'user': session['username']}))
            if len(res)!=0:
                general_rating_avg = general_rating / len(res)
            else:
                general_rating_avg = 0
            return render_template('performance.html', msg="Quiz deleted successfully!", username=session['username'], 
                                   results=result, 
                                   resul=r,
                                   this_week=this_week, 
                                   this_month=this_month, 
                                   general_rating=general_rating_avg, 
                                   all_quizzes_solved=all_quizzes_solved)
    else:
        return render_template('performance.html', err="Error!", username=session['username'], 
                               results=[], 
                               resul=[], 
                               this_week=0, 
                               this_month=0, 
                               general_rating=0, 
                               all_quizzes_solved=0)
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')