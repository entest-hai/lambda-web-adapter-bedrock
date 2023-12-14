---
title: lambda web adapter bedrock integration
author: haimtran
description: use lambda web adapter to integrate with bedrock
publishedDate: 14 DEC 2023
---

## Lambda Web Adapter

Let create a lambda function with web adatper enabled. Please pay attention to the permissions so this function can call Bedrock

```ts
import { Stack, StackProps, aws_iam, aws_lambda } from "aws-cdk-lib";
import { Effect } from "aws-cdk-lib/aws-iam";
import { Construct } from "constructs";
import path = require("path");

export class LambdaWebAdapter extends Stack {
  constructor(scope: Construct, id: string, props: StackProps) {
    super(scope, id, props);

    const func = new aws_lambda.Function(this, "FlaskWebAdapter", {
      functionName: "FlaskWebAdatper",
      code: aws_lambda.EcrImageCode.fromAssetImage(
        path.join(__dirname, "./../../flask/app/")
      ),
      runtime: aws_lambda.Runtime.FROM_IMAGE,
      handler: aws_lambda.Handler.FROM_IMAGE,
      memorySize: 1024,
    });

    func.addToRolePolicy(
      new aws_iam.PolicyStatement({
        effect: Effect.ALLOW,
        resources: [
          "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-v2",
        ],
        actions: [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream",
        ],
      })
    );
  }
}
```

## Bedrock API

Let call batch response

```py
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
```

Let call stream response

```py
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
```

## FrontEnd

Let create a simple javascript client to handle

```js
onst callBedrock = async () => {
  const topic = document.getElementById("topic").value;
  storyOutput.innerText = "thinking ...";
  console.log("call bedrock request", topic);

  if (topic) {
    try {
      const response = await fetch("/bedrock", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ topic: topic }),
      });
      const body = await response.json();
      console.log(body);
      storyOutput.innerText = body.completion;
    } catch (error) {
      console.log(error);
    }
  }
};
```

Client which handle stream response from Bedrock

```js
const callBedrockStream = async () => {
  console.log("call bedrock request");

  try {
    const response = await fetch("/bedrock-stream", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ topic: "chicken soup" }),
    });

    console.log(response);
    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        break;
      }
      const text = decoder.decode(value);
      console.log(text);
      storyOutput.innerText += text;
    }
  } catch (error) {
    console.log(error);
  }
};
```

## Reference

- [Using response streaming with AWS Lambda Web Adapter to optimize performance](https://aws.amazon.com/blogs/compute/using-response-streaming-with-aws-lambda-web-adapter-to-optimize-performance/)

- [Lifting and shifting a web application to AWS Serverless: Part 1](https://aws.amazon.com/blogs/compute/lifting-and-shifting-a-web-application-to-aws-serverless-part-1/)

- [Lifting and shifting a web application to AWS Serverless: Part 2](https://aws.amazon.com/blogs/compute/lifting-and-shifting-a-web-application-to-aws-serverless-part-2/)

- [aws-lambda-web-adapter](https://github.com/awslabs/aws-lambda-web-adapter)
