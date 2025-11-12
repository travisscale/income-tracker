# 1. 导入所有需要的库
import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, flash
from werkzeug.utils import secure_filename

# 2. 初始化 Flask 应用
app = Flask(__name__)

# --- 核心配置区 ---

# 3. 设置 SECRET_KEY (这是修复错误的关键！)
#    这是 Flask session 工作所必需的加密密钥。
#    请务-必把它换成一个没人知道的、复杂的字符串！
app.secret_key = 'qazplm714119'

# 4. 设置你的管理员密码
#    为了简单起见，我们直接写在这里。
ADMIN_PASSWORD = '18580508131' # <-- 在这里修改成你的真实密码！

# 5. 设置文件上传的目标文件夹
UPLOAD_FOLDER = 'shared_files'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 6. 使用一个全局变量来追踪当前分享的文件名列表
#    这种方式简单，并且在 Render 的临时文件系统上能正常工作。
CURRENT_FILENAMES = []


# --- 路由和视图函数 ---

# 主页路由 (现在受登录保护)
@app.route('/')
def index():
    # 在显示主页之前，检查 session 里有没有 "logged_in" 这个记号
    if not session.get('logged_in'):
        # 如果没有，说明用户没登录，把他重定向到登录页面
        return redirect(url_for('login'))
    
    # 如果用户已经登录，才显示主页，并把文件名列表传递给模板
    return render_template('index.html', filenames=CURRENT_FILENAMES)

# 文件上传路由 (分离出来，同样受登录保护)
@app.route('/upload', methods=['POST'])
def upload_files():
    global CURRENT_FILENAMES # 声明我们要修改的是全局变量
    
    # 再次检查是否登录，防止有人直接访问这个URL
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    uploaded_files = request.files.getlist('file')

    if not uploaded_files or uploaded_files[0].filename == '':
        flash('未选择任何文件。', 'warning') # 使用 flash 显示提示信息
        return redirect(url_for('index'))
    
    # --- 核心逻辑：先删除所有旧文件 ---
    for filename in CURRENT_FILENAMES:
        old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(old_file_path):
            os.remove(old_file_path)
    
    # 清空记录文件名的列表
    CURRENT_FILENAMES.clear()

    # 循环处理并保存所有新上传的文件
    for file in uploaded_files:
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # 将新文件名追加到列表中
            CURRENT_FILENAMES.append(filename)
    
    flash('文件已成功更新！', 'success')
    return redirect(url_for('index'))

# 登录路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    # 如果用户提交了表单 (POST请求)
    if request.method == 'POST':
        password_attempt = request.form['password']
        if password_attempt == ADMIN_PASSWORD:
            # 密码正确，在 session 里做一个记号，表示“已登录”
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            # 密码错误，通过 flash 显示一条错误消息
            flash('密码错误，请重试！', 'danger')
            
    # 如果是初次访问 (GET请求) 或密码错误，就显示登录页面
    return render_template('login.html')

# 登出路由
@app.route('/logout')
def logout():
    # 从 session 中移除 "logged_in" 这个记号
    session.pop('logged_in', None)
    flash('您已成功登出。', 'info')
    return redirect(url_for('login'))

# 文件下载路由 (保持公开，任何人都可以下载)
@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


# --- 程序入口 ---
if __name__ == '__main__':
    # 允许局域网访问，并关闭 reloader 以兼容某些环境
    app.run(host='0.0.0.0', port=5000, debug=True)