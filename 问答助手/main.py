"""问答助手入口文件 - 支持记忆功能"""
import uuid
from workflow import create_search_assistant
from langchain_core.messages import HumanMessage


def main():
    print("🤖 欢迎使用问答助手！")
    print("====================\n")
    print("💡 我会记住我们的对话，可以连续提问哦~\n")
    
    # 创建工作流
    app = create_search_assistant()
    
    # 生成唯一的线程ID（保持不变以记住对话历史）
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    conversation_count = 0
    
    while True:
        user_input = input(f"[对话 {conversation_count + 1}] 请输入您的问题（输入 'exit' 或 'quit' 退出）：\n")
        
        if user_input.lower() in ['exit', 'quit', '退出']:
            print("👋 感谢使用问答助手，再见！")
            break
        
        if not user_input.strip():
            print("❌ 请输入有效问题")
            continue
        
        print("\n🔄 正在处理您的问题...\n")
        
        try:
            # 调用工作流（使用相同的config保持记忆）
            result = app.invoke(
                {"messages": [HumanMessage(content=user_input)]},
                config=config
            )
            
            # 输出结果
            print("✅ 回答：")
            print(result["final_answer"])
            print("\n" + "="*50 + "\n")
            
            conversation_count += 1
            
        except Exception as e:
            print(f"❌ 发生错误：{str(e)}")
            print("\n" + "="*50 + "\n")


if __name__ == "__main__":
    main()