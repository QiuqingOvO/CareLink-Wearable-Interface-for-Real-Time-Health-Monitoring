from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify,Response
from openai import OpenAI
from config import API_CONFIG
#from db_config import DB_CONFIG
import json
from flask import jsonify, send_from_directory
import os
import mysql.connector
import hashlib
import pandas as pd
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
client = OpenAI(
    api_key=API_CONFIG["api_key"],
    base_url=API_CONFIG["base_url"]
)


db_CONFIG = {
    'host': 'localhost',
    'user': 'root', 
    'password': 'root',
    'database': 'miband'
}

def get_db_connection():
    return mysql.connector.connect(**db_CONFIG)

def hash_password(password):
    """对密码进行哈希加密处理"""
    return hashlib.sha256(password.encode()).hexdigest()


# 登录页面
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    '''if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hash_password(password)

        # 临时测试用的用户名和密码
        if username == "test" and password == "test":
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash("Wrong username or password", "error")
            return redirect(url_for('login'))'''
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hash_password(password)
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', 
                         (username, hashed_password))
            user = cursor.fetchone()
            
            if user:
                session['username'] = username
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong username or password", "error")
                return redirect(url_for('login'))
        finally:
            cursor.close()
            conn.close()
    


    return render_template('login.html')

# 添加额外的静态文件夹路径
@app.route('/image/<path:filename>')
def image(filename):
    image_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'image')
    return send_from_directory(image_dir, filename)

# 注册页面
@app.route('/register', methods=['GET', 'POST'])

def register():
    '''if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("The two passwords are not the same", "error")
            return redirect(url_for('register'))

        flash("Register successfully, please login", "success")
        return redirect(url_for('login'))

    return render_template('register.html')'''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        security_answer = request.form['security_answer']

        if password != confirm_password:
            flash("The two passwords are not the same", "error")
            return redirect(url_for('register'))

        hashed_password = hash_password(password)
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('INSERT INTO users (username, password, security_answer) VALUES (%s, %s, %s)',
                           (username, hashed_password, security_answer))
            conn.commit()
            flash("Register successfully, please login", "success")
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash("Username already exists", "error")
            return redirect(url_for('register'))
        finally:
            cursor.close()
            conn.close()

    return render_template('register.html')


# 忘记密码页面
@app.route('/forget', methods=['GET', 'POST'])
def forget():
    '''if request.method == 'POST':
        username = request.form['username']
        security_answer = request.form['security_answer']
        new_password = request.form['new_password']
        confirm_new_password = request.form['confirm_new_password']

        if new_password != confirm_new_password:
            flash("The two passwords do not match", "error")
            return redirect(url_for('forget'))

        # 这里应查询数据库判断用户名是否存在，并验证密保答案是否正确，
        # 然后更新密码（注意密码更新时应进行加密处理）。
        # 以下为伪代码示例：
        #
        # user = User.query.filter_by(username=username).first()
        # if user and user.security_answer == security_answer:
        #     user.password = hash_password(new_password)
        #     db.session.commit()
        #     flash("Password reset successfully, please login", "success")
        #     return redirect(url_for('login'))
        # else:
        #     flash("Incorrect username or security answer", "error")
        #     return redirect(url_for('forget'))

        # 当前使用测试数据判断
        if username == "test" and security_answer == "test_answer":
            flash("Password reset successfully, please login", "success")
            return redirect(url_for('login'))
        else:
            flash("Incorrect username or security answer", "error")
            return redirect(url_for('forget'))
    return render_template('forget.html')'''

    if request.method == 'POST':
        username = request.form['username']
        security_answer = request.form['security_answer']
        new_password = request.form['new_password']
        confirm_new_password = request.form['confirm_new_password']

        if new_password != confirm_new_password:
            flash("The two new passwords are not the same", "error")
            return redirect(url_for('forget'))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute('SELECT * FROM users WHERE username = %s AND security_answer = %s',
                           (username, security_answer))
            user = cursor.fetchone()

            if user:
                hashed_password = hash_password(new_password)
                cursor.execute('UPDATE users SET password = %s WHERE username = %s',
                               (hashed_password, username))
                conn.commit()
                flash("Password reset successfully, please login", "success")
                return redirect(url_for('login'))
            else:
                flash("Wrong username or security answer", "error")
                return redirect(url_for('forget'))
        finally:
            cursor.close()
            conn.close()

    return render_template('forget.html')

# 仪表盘页面
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session.get('username'))


# 连接手环页面
@app.route('/connect')
def connect():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('connect.html')

# 心率监测页面
@app.route('/heart-rate')
def heart_rate():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('heart_rate.html')

# 步数统计页面
@app.route('/steps')
def steps():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('step.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')


# 睡眠监测页面
@app.route('/sleep')
def sleep():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('sleep.html')

@app.route('/heartrate')
def heartrate():
    import requests
    try:
        # 这个URL会被heartrate.py自动更新为正确的端口
        response = requests.get('http://127.0.0.1:3030/heartrate')
        heart_rate = response.text  # 直接获取文本，不是JSON
        return str(heart_rate)
    except Exception as e:
        print(f"Fail to get the heart rate data: {e}")
        # 如果无法连接到外部程序，返回一个默认值
        return "Fail"


# 添加favicon路由
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


# 添加基本的安全头
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response


@app.route('/')
def home():
    return render_template('index.html')


def get_api_response(user_message, max_retries=3):
    """获取API响应，支持重试机制"""
    for attempt in range(max_retries):
        try:
            print(f"\n第{attempt + 1}次尝试获取回答")
            response = client.chat.completions.create(
                model='deepseek-reasoner',
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_message},
                ],
                stream=True
            )

            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content

            if full_response.strip():  # 如果有实际内容就返回
                print(f"\n完整回答: {full_response}\n")
                return
            else:
                print(f"\n第{attempt + 1}次尝试返回为空")

        except Exception as e:
            print(f"\n第{attempt + 1}次尝试发生错误: {str(e)}")
            if attempt == max_retries - 1:  # 最后一次尝试
                raise Exception("API多次调用失败")

    raise Exception("API返回数据为空")


@app.route('/chat_reply', methods=['POST'])
def chat_reply():
    try:
        user_message = request.json['message']
        print(f"\n用户问题: {user_message}")

        def generate():
            full_response = ""  # 在循环外初始化
            for attempt in range(3):  # 最多尝试3次
                try:
                    print(f"\n第{attempt + 1}次尝试获取回答")
                    response = client.chat.completions.create(
                        model='deepseek-reasoner',
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": user_message},
                        ],
                        stream=True
                    )
                    for chunk in response:
                        if chunk.choices[0].delta.content is not None:
                            content = chunk.choices[0].delta.content
                            full_response += content
                            print(content, end='', flush=True)
                            yield f"data: {json.dumps({'content': content})}\n\n"
                    if full_response.strip():  # 如果响应不为空，则返回
                        print(f"\n完整回答: {full_response}")
                        return
                    else:
                        print(f"\n第{attempt + 1}次尝试返回为空")
                except Exception as e:
                    print(f"\n第{attempt + 1}次尝试发生错误: {str(e)}")
                    if attempt == 2:  # 最后一次尝试失败
                        yield f"data: {json.dumps({'content': '**API返回数据为空**'})}\n\n"
            if not full_response.strip():
                yield f"data: {json.dumps({'content': '**API返回数据为空**'})}\n\n"

        return Response(generate(), mimetype='text/event-stream')
    except Exception as e:
        error_msg = f"发生错误: {str(e)}"
        print(error_msg)
        return jsonify({"error": error_msg}), 500


    '''except Exception as e:
        error_msg = f"发生错误: {str(e)}"
        print(error_msg)
        return jsonify({"error": error_msg}), 500'''
    
    

# 添加处理步数数据上传的路由
@app.route('/upload_steps', methods=['POST'])
def upload_steps():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    if file and file.filename.endswith('.csv'):
        try:
            df = pd.read_csv(file)
            if 'date' not in df.columns or 'steps' not in df.columns:
                return jsonify({'error': 'CSVfile is not correct'}), 400
                
            # 处理数据
            data = {
                'dates': df['date'].tolist(),
                'steps': df['steps'].tolist()
            }
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
    
    return jsonify({'error': 'Only CSV files are supported'}), 400

# 添加处理睡眠数据上传的路由
@app.route('/upload_sleep', methods=['POST'])
def upload_sleep():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    if file and file.filename.endswith('.csv'):
        try:
            df = pd.read_csv(file)
            required_columns = ['date', 'totalSleep', 'deepSleep', 'lightSleep', 
                              'remSleep', 'awakeSleep', 'sleepScore', 'sleepQuality']
            
            if not all(col in df.columns for col in required_columns):
                return jsonify({'error': 'CSVfile is not correct'}), 400
                
            # 处理数据
            data = {col: df[col].tolist() for col in required_columns}
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
    
    return jsonify({'error': 'Only CSV files are supported'}), 400

if __name__ == '__main__':
    app.run(debug=True)
