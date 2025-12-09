from curator import client, MODEL_NAME
import sys

def test_connection():
    print("--- 开始测试火山方舟 API 连接 ---")
    
    if not client:
        print("错误: Client 未初始化。请检查 API Key 配置。")
        return

    print(f"当前模型: {MODEL_NAME}")
    # print(f"Client Base URL: {client.base_url}")

    try:
        print("正在发送测试请求...")
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "你好，请回复'火山方舟测试成功'。"}
            ]
        )
        content = response.choices[0].message.content
        print(f"\nAPI 响应:\n{content}")
        print("\n--- 测试完成 ---")
    except Exception as e:
        print(f"\n测试失败: {e}")

if __name__ == "__main__":
    test_connection()
