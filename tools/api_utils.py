import random
import time


# API重试机制
def retry_api_call(func, max_retries=10, delay=2, *args, **kwargs):
    for attempt in range(max_retries):
        try:
            print(f"尝试第 {attempt + 1} 次API调用...")
            result = func(*args, **kwargs)
            print(f"API调用成功")
            return result
        except Exception as e:
            error_msg = str(e)
            print(f"API调用失败 (尝试 {attempt + 1}/{max_retries}): {error_msg}")

            if "504" in error_msg or "timeout" in error_msg.lower() or "gateway" in error_msg.lower():
                if attempt < max_retries - 1:
                    wait_time = delay * (2 ** attempt) + random.uniform(0, 1)  # 指数退避
                    print(f"等待 {wait_time:.1f} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"达到最大重试次数，API调用失败")
                    raise e
            else:
                # 非超时错误，直接抛出
                raise e

    raise Exception("API调用失败，已达到最大重试次数")


# 安全的Agent调用包装器
def safe_agent_call(agent, method_name, *args, **kwargs):
    method = getattr(agent, method_name)
    return retry_api_call(method, *args, **kwargs)
