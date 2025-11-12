import os
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd

# 初始化 Flask 应用
app = Flask(__name__)

# 设置一个上传文件的保存目录 (虽然我们不永久保存，但上传过程中需要一个临时位置)
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 允许上传的文件类型
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    """检查文件名后缀是否在允许的范围内"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 网站主页，现在是上传页面
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    # 如果是 POST 请求，意味着用户提交了文件
    if request.method == 'POST':
        # 检查请求中是否包含文件部分
        if 'file' not in request.files:
            return redirect(request.url) # 如果没有文件，刷新页面
        
        file = request.files['file']

        # 如果用户没有选择文件，浏览器可能会提交一个空文件名
        if file.filename == '':
            return redirect(request.url)

        # 如果文件存在且类型正确
        if file and allowed_file(file.filename):
            try:
                # 直接用 pandas 从上传的文件流中读取 Excel 数据
                # 不需要真的把文件保存到服务器硬盘上，更高效、更安全
                df = pd.read_excel(file)

                # --- 核心计算逻辑 ---
                # 确保Excel至少有三列
                if df.shape[1] < 3:
                    error_message = "上传的 Excel 文件必须至少包含 A, B, C 三列。"
                    return render_template('error.html', error=error_message)

                # 选择 A, B, C 三列 (在 pandas 中索引从0开始)
                col_a = df.iloc[:, 0]
                col_b = df.iloc[:, 1]
                col_c = df.iloc[:, 2]

                # 将列中非数字的内容转换为空值(NaN)，然后求和
                sum_a = pd.to_numeric(col_a, errors='coerce').sum()
                sum_b = pd.to_numeric(col_b, errors='coerce').sum()
                sum_c = pd.to_numeric(col_c, errors='coerce').sum()

                # 渲染结果页面，并把计算结果传递过去
                return render_template('result.html', 
                                       sum_a=f"{sum_a:,.2f}", 
                                       sum_b=f"{sum_b:,.2f}", 
                                       sum_c=f"{sum_c:,.2f}")

            except Exception as e:
                # 如果pandas读取失败或计算出错，显示一个错误页面
                error_message = f"处理文件时出错: {e}。请确保上传的是有效的 Excel 文件，且 A-C 列包含数字。"
                return render_template('error.html', error=error_message)

    # 如果是 GET 请求，就显示上传表单
    return render_template('upload.html')


if __name__ == '__main__':
    app.run(debug=True)