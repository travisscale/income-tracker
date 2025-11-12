import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)

# --- 关键改动 1: 添加配置 ---
# 1. 设置一个 SECRET_KEY，这是 Flask Session 工作所必需的。
#    请务必把它换成一个没人知道的、复杂的字符串！
app.secret_key = os.environ.get('qazplm714119')
ADMIN_PASSWORD = os.environ.get('18580508131')

# 2. 在这里硬编码你的管理员密码
#    未来可以改成从环境变量读取，以提高安全性
ADMIN_PASSWORD = 'your_password_here' # <-- 请修改成你的密码！

# 3. 文件上传的文件夹配置
UPLOAD_FOLDER = 'shared_files'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 4. 用一个全局变量来追踪文件名（这种方式在Render上工作良好）
CURRENT_FILENAMES = []

# --- 路由 ---

@app.route('/')
def index():
    # --- 关键改动 2: 保护主页 ---
    # 在显示主页之前，检查 session 里有没有 "logged_in" 这个记号
    if not session.get('logged_in'):
        # 如果没有，说明用户没登录，把他重定向到登录页面
        return redirect(url_for('login'))
    
    # 如果用户已经登录，才显示主页
    return render_template('index.html', filenames=CURRENT_FILENAMES)


@app.route('/upload', methods=['POST'])
def upload_files():
    global CURRENT_FILENAMES
    # --- 关键改动 3: 将上传逻辑分离并加以保护 ---
    if not session.get('logged_in'):
        return redirect(url_for('login')) # 未登录用户不能上传

    uploaded_files = request.files.getlist('file')
    if not uploaded_files or uploaded_files[0].filename == '':
        flash('No files selected for upload.', 'warning')
        return redirect(url_for('index'))
    
    for filename in CURRENT_FILENAMES:
        old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(old_file_path):
            os.remove(old_file_path)
    
    CURRENT_FILENAMES.clear()

    for file in uploaded_files:
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            CURRENT_FILENAMES.append(filename)
    
    flash('Files have been successfully updated!', 'success')
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    # --- 关键改动 4: 创建登录路由 ---
    if request.method == 'POST':
        # 用户提交了密码
        password_attempt = request.form['password']
        if password_attempt == ADMIN_PASSWORD:
            # 密码正确，在 session 里做个记号
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            # 密码错误，通过 flash 显示一条错误消息
            flash('Invalid password!', 'danger')
    # 如果是 GET 请求，或者密码错误，就显示登录页面
    return render_template('login.html')


@app.route('/logout')
def logout():
    # --- 关键改动 5: 创建登出路由 ---
    # 从 session 中移除 "logged_in" 这个记号
    session.pop('logged_in', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/download/<path:filename>')
def download_file(filename):
    # 下载功能保持公开，任何人都可以下载
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)