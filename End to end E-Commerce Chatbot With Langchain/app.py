from flask import Flask, render_template, request
from dotenv import load_dotenv
from ecombot.retrieval_generation import generation
from ecombot.ingest import ingest_data

app = Flask(__name__)

load_dotenv()

vector_store = ingest_data("done")
chain = generation(vector_store)

@app.route("/")
def index():
    return render_template('chat.html')

@app.route("/get", methods=["GET","POST"])
def chat():
    input = request.form['msg']
    result = chain.invoke(input)

    print({"Response": result})

    return str(result)


if __name__ == "__main__":
    app.run(debug=True)