from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/')
def index():
    query_params = request.args.to_dict()
    return jsonify({
        "message": "Получены параметры",
        "params": query_params
    })


if __name__ == '__main__':
    app.run(debug=True)
