import boto3
from flask import (Flask, jsonify, render_template, request)
import json

bedrock_client = boto3.client('bedrock-runtime')

app = Flask(__name__)

app.jinja_env.auto_reload = True
app.config["TEMPLATES_AUTO_RELOAD"] = True

# get book list should be even number
with open("./static/book.json", "rb") as file:
    books = json.load(file)

@app.route('/', methods=['GET', 'POST'])
def hello():
    return render_template('bedrock.html')
    # return jsonify(status=200, message='hello world')


@app.route('/home')
def home():
    return render_template('index.html', books=books, nrow=len(books))


@app.route("/bedrock", methods= ['GET', 'POST'])
def bedrock_batch(topic='chicken soup'):
    """
    demo
    """

    if request.method == 'POST':
        topic = request.json.get('topic') 
        print(request.json.get('topic'))
    else:
        print('get')

    # prompt 
    instruction = f"""
    You are a world class writer. Please write a sweet bedtime story about {topic}.
    """
    # body  
    body = json.dumps({
        'prompt': f'Human:{instruction}\n\nAssistant:', 
        'max_tokens_to_sample': 1028,
        'temperature': 1,
        'top_k': 250,
        'top_p': 0.999,
        'stop_sequences': ['\n\nHuman:']
    })
    # bedrock request 
    response = bedrock_client.invoke_model(
        body=body,
        contentType="application/json",
        accept="*/*",
        modelId="anthropic.claude-v2",
    )
    # bedrock response 
    response_body = json.loads(
        response.get('body').read()
    )
    print(response_body)
    # resposne 
    return response_body


@app.route('/bedrock-stream', methods = ['GET', 'POST'])
def bedrock_stream(topic:str ='chicken soup'):
    """
    demo
    """
    
    instruction = f'You are a world class writer. Please write a sweet bedtime story about {topic}'
    # request body
    body = json.dumps({
        'prompt': f'Human:{instruction}\n\nAssistant:', 
        'max_tokens_to_sample': 1028,
        'temperature': 1,
        'top_k': 250,
        'top_p': 0.999,
        'stop_sequences': ['\n\nHuman:']
    })
    # response
    response = bedrock_client.invoke_model_with_response_stream(
        body=body,
        contentType="application/json",
        accept="*/*",
        modelId="anthropic.claude-v2",
    )
    # parse stream
    stream = response.get('body')
    if stream:
        for event in stream:
            chunk = event.get('chunk')
            if chunk:
                yield json.loads(chunk.get('bytes').decode())['completion']


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)