import boto3

from browsing import browsing

AWS_ACCESS_KEY = ''
AWS_SECRET_KEY = ''
AWS_REGION = ''

bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
)

message_list = []

initial_message = {
    "role": "user",
    "content": [
        {"text": "https://openai.com/ 여기서 최신 뉴스의 제목이 무엇인가요?"}
    ],
}

message_list.append(initial_message)

tool_list = [
    {
        "toolSpec": {
            "name": "browsing",
            "description": "Try web browsing",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "url address"
                        }
                    },
                    "required": ["url"]
                }
            }
        }
    }
]

response = bedrock_client.converse(
    modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
    messages=message_list,
    toolConfig={
        "tools": tool_list
    },
)

output_message = response['output']['message']
message_list.append(output_message)
stop_reason = response['stopReason']

# Using browsing() on another file
# def browsing(url):
#     return "Test Content"


if stop_reason == 'tool_use':
    follow_up_content_blocks = []

    for content_block in response['output']['message']['content']:
        if 'toolUse' in content_block:
            tool_use_block = content_block['toolUse']
            tool_use_name = tool_use_block['name']

            if tool_use_name == 'browsing':
                url = tool_use_block['input']['url']

                content = browsing(url)

                follow_up_content_blocks.append({
                    "toolResult": {
                        "toolUseId": tool_use_block['toolUseId'],
                        "content": [
                            {
                                "json": {
                                    "result": content
                                }
                            }
                        ]
                    }
                })

    if len(follow_up_content_blocks) > 0:
        follow_up_message = {
            "role": "user",
            "content": follow_up_content_blocks,
        }

        message_list.append(follow_up_message)

    response = bedrock_client.converse(
        modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
        messages=message_list,
        toolConfig={
            "tools": tool_list
        },
    )

    output_message = response['output']['message']
    message_list.append(output_message)
    stop_reason = response['stopReason']

print(output_message)
