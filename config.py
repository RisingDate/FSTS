import os

# API Keys and Environment Variables
os.environ["IFLYTEK_SPARK_APP_ID"] = "your_spark_app_id_here"
os.environ["IFLYTEK_SPARK_API_SECRET"] = "your_spark_api_secret_here"
os.environ["IFLYTEK_SPARK_API_KEY"] = "your_spark_api_key_here"

os.environ["OPENAI_API_KEY"] = "your_openai_api_key_here"
os.environ["OPENAI_BASE_URL"] = "your_openai_base_url_here"

os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_ENDPOINT'] = "https://api.smith.langchain.com"
os.environ['LANGCHAIN_API_KEY'] = "your_langchain_api_key_here"
os.environ['LANGCHAIN_PROJECT'] = "your_project_name_here"

# Model whitelists
OLLAMA_MODEL_LIST = {
    'think': ['deepseek-r1:32b', 'deepseek-r1:32b-qwen-distill-q8_0'],
    'nothink': ['gpt-4o', 'gpt-5-mini']
}
