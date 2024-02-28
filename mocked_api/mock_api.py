import json
import re
import time
import uuid
import warnings

from lorem_text import lorem

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# add CORS middleware to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define a route to handle POST requests
@app.post("/v1/chat/completions")
async def post_data(data: dict):
    """Returns mock responses for testing purposes."""

    messages = data['messages']
    model = data['model']
    instructions = messages[-1]['content']

    delay = 0
    lines = None
    answer = 'Default mock answer from mocked API'

    try:
        delay = re.findall(r'(?<=d)\d+', instructions)[0]
    except:
        pass

    try:
        lines = re.findall(r'(?<=l)\d+', instructions)[0]
    except:
        pass

    if delay:
        time.sleep(int(delay))
    
    if data['stream']:
        warnings.warn('streaming.....')

        async def iter(lines):
            id = f"chatcmpl-{uuid.uuid4()}"
            lines = lines or 1
            print(lines)
            for _ in range(int(lines)):
                sentence = lorem.sentence()
                # todo: use tokenizer to split by token ~ 4 chars
                for word in sentence.split(' '):
                    data = {
                        "id": id,
                        "object": "chat.completion.chunk",
                        "created": time.time(),
                        "model": model,
                        "choices": [
                            {
                                "index": 0,
                                "delta": {
                                    "content": word
                                },
                                "finish_reason": "null"
                            }
                        ]
                    }
                    msg = f"data: {json.dumps(data)}\n\n"
                    time.sleep(0.1)
                    yield str.encode(msg)
            print(f'Latest id before end: {id}')
            last_msg = json.dumps({
                "id": id,
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {},
                        "finish_reason": "done"
                    }
                ]
            })
            last_msg = f"data: {last_msg}\n\n"
            print(f'Last message: {last_msg}')
            yield str.encode(last_msg)
            yield b'data: [DONE]\n\n'

        return StreamingResponse(
            content=iter(lines),
            status_code=200,
            media_type="text/event-stream"
        )

    if lines:
        answer = "\n".join([lorem.sentence() for _ in range(int(lines))])

    response = {
        "id": 0,
        "choices": [{
            "index": 0,
            "finish_reason": "stop",
            "message": {"content": answer, "role": "assistant"}
        }]
    }
    return response


@app.get('/v1/models')
async def list_models():
    """Returns a list of models to get app to work."""
    with open('/work/models_response.json') as f:
        result = json.load(f)

    return result


@app.post('/')
async def post_data(data: dict):
    """Basic route for testing the API works"""
    result = {"message": "Data received", "data": data}
    return result
