from app.llm.bedrock_client import get_llm

llm = get_llm()

response = llm.invoke("Say 'Bedrock is working' in one sentence.")
print(response.content)
