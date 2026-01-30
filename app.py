from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    # TODO: EAD to MARC conversion logic
    return {'status': 'not implemented yet'}

if __name__ == '__main__':
    app.run(debug=True)
