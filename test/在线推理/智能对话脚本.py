"""
vLLM 智能对话脚本
提供交互式命令行界面，支持多轮对话、历史记录、流式输出等功能

功能特性:
    - 🤖 多轮对话，自动维护上下文
    - 📝 对话历史记录
    - 🎨 彩色输出，美化界面
    - 💾 保存/加载对话历史
    - ⚙️ 动态调整参数（温度、长度等）
    - 🔄 支持流式和非流式输出
    - 📊 显示 token 使用统计

使用方法:
    python 智能对话脚本.py
    
    命令列表:
        /help       - 显示帮助信息
        /clear      - 清空对话历史
        /history    - 显示对话历史
        /save       - 保存对话到文件
        /load       - 加载对话历史
        /config     - 查看/修改配置
        /stream     - 切换流式输出
        /quit       - 退出程序

作者: AI Assistant
日期: 2025-10-08
"""

import sys
import os
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

# 添加父目录到路径以导入 vllm_client
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vllm_client import VLLMClient


# ============ 颜色输出工具 ============

class Colors:
    """ANSI 颜色代码"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # 前景色
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # 亮色
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'


def print_colored(text: str, color: str = Colors.RESET, bold: bool = False):
    """彩色打印"""
    prefix = Colors.BOLD if bold else ""
    print(f"{prefix}{color}{text}{Colors.RESET}")


def print_box(text: str, color: str = Colors.CYAN):
    """打印带边框的文本"""
    lines = text.split('\n')
    max_len = max(len(line) for line in lines)
    
    print_colored("┌" + "─" * (max_len + 2) + "┐", color)
    for line in lines:
        padding = " " * (max_len - len(line))
        print_colored(f"│ {line}{padding} │", color)
    print_colored("└" + "─" * (max_len + 2) + "┘", color)


# ============ 智能对话类 ============

class SmartChat:
    """智能对话管理器"""
    
    def __init__(
        self,
        base_url: str = "http://localhost:9000",
        api_key: str = "muyu",
        model: str = "Medical_Qwen3_8B_Large_Language_Model",
        backend: str = 'openai'  # 默认使用 openai 后端支持流式输出
    ):
        """初始化对话管理器"""
        self.client = VLLMClient(
            base_url=base_url,
            api_key=api_key,
            model=model,
            backend=backend
        )
        
        self.messages: List[Dict[str, str]] = []
        self.config = {
            'max_tokens': 512,
            'temperature': 0.7,
            'top_p': 0.95,
            'stream': True,  # 默认开启流式输出
            'backend': backend
        }
        
        self.history_dir = Path("chat_history")
        self.history_dir.mkdir(exist_ok=True)
        
        self.total_tokens_used = 0
    
    def add_message(self, role: str, content: str):
        """添加消息到历史"""
        self.messages.append({
            "role": role,
            "content": content
        })
    
    def clear_history(self):
        """清空对话历史"""
        self.messages.clear()
        self.total_tokens_used = 0
        print_colored("✅ 对话历史已清空", Colors.GREEN)
    
    def show_history(self):
        """显示对话历史"""
        if not self.messages:
            print_colored("📭 暂无对话历史", Colors.YELLOW)
            return
        
        print_colored("\n" + "=" * 60, Colors.CYAN)
        print_colored("📜 对话历史", Colors.CYAN, bold=True)
        print_colored("=" * 60, Colors.CYAN)
        
        for i, msg in enumerate(self.messages, 1):
            role = msg['role']
            content = msg['content']
            
            if role == 'user':
                print_colored(f"\n[{i}] 👤 用户:", Colors.BRIGHT_BLUE, bold=True)
                print(f"    {content}")
            else:
                print_colored(f"\n[{i}] 🤖 助手:", Colors.BRIGHT_GREEN, bold=True)
                print(f"    {content}")
        
        print_colored("\n" + "=" * 60 + "\n", Colors.CYAN)
    
    def save_history(self, filename: Optional[str] = None):
        """保存对话历史到文件"""
        if not self.messages:
            print_colored("❌ 没有对话历史可保存", Colors.RED)
            return
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chat_{timestamp}.json"
        
        filepath = self.history_dir / filename
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'config': self.config,
            'messages': self.messages,
            'total_tokens': self.total_tokens_used
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print_colored(f"✅ 对话已保存到: {filepath}", Colors.GREEN)
    
    def load_history(self, filename: str):
        """从文件加载对话历史"""
        filepath = self.history_dir / filename
        
        if not filepath.exists():
            print_colored(f"❌ 文件不存在: {filepath}", Colors.RED)
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.messages = data.get('messages', [])
            self.total_tokens_used = data.get('total_tokens', 0)
            
            print_colored(f"✅ 已加载 {len(self.messages)} 条对话记录", Colors.GREEN)
        except Exception as e:
            print_colored(f"❌ 加载失败: {e}", Colors.RED)
    
    def list_saved_chats(self):
        """列出已保存的对话"""
        files = sorted(self.history_dir.glob("chat_*.json"), reverse=True)
        
        if not files:
            print_colored("📭 没有已保存的对话", Colors.YELLOW)
            return
        
        print_colored("\n📚 已保存的对话:", Colors.CYAN, bold=True)
        for i, file in enumerate(files[:10], 1):  # 只显示最近10个
            size = file.stat().st_size
            mtime = datetime.fromtimestamp(file.stat().st_mtime)
            print(f"  {i}. {file.name} ({size} bytes, {mtime.strftime('%Y-%m-%d %H:%M')})")
        print()
    
    def show_config(self):
        """显示当前配置"""
        print_colored("\n⚙️  当前配置:", Colors.CYAN, bold=True)
        print_colored("─" * 40, Colors.CYAN)
        for key, value in self.config.items():
            print(f"  {key:15s} = {value}")
        print_colored("─" * 40 + "\n", Colors.CYAN)
    
    def update_config(self, key: str, value):
        """更新配置"""
        if key not in self.config:
            print_colored(f"❌ 未知配置项: {key}", Colors.RED)
            return
        
        # 类型转换
        try:
            if key == 'max_tokens':
                value = int(value)
            elif key in ['temperature', 'top_p']:
                value = float(value)
            elif key == 'stream':
                value = value.lower() in ['true', '1', 'yes', 'on']
            
            self.config[key] = value
            print_colored(f"✅ 已更新: {key} = {value}", Colors.GREEN)
        except ValueError as e:
            print_colored(f"❌ 无效的值: {e}", Colors.RED)
    
    def chat(self, user_input: str) -> str:
        """发送消息并获取回复"""
        self.add_message("user", user_input)
        
        try:
            if self.config['stream'] and self.config['backend'] == 'openai':
                # 流式输出
                print_colored("\n🤖 助手: ", Colors.BRIGHT_GREEN, bold=True)
                
                response_text = ""
                for chunk in self.client.chat_stream_with_history(
                    self.messages,
                    max_tokens=self.config['max_tokens'],
                    temperature=self.config['temperature'],
                    top_p=self.config['top_p']
                ):
                    print(chunk, end="", flush=True)
                    response_text += chunk
                
                print("\n")
                self.add_message("assistant", response_text)
                return response_text
            else:
                # 非流式输出
                response = self.client.chat_with_history(
                    self.messages,
                    max_tokens=self.config['max_tokens'],
                    temperature=self.config['temperature'],
                    top_p=self.config['top_p']
                )
                
                self.add_message("assistant", response)
                return response
        
        except Exception as e:
            print_colored(f"\n❌ 错误: {e}", Colors.RED)
            # 移除失败的用户消息
            self.messages.pop()
            return ""
    
    def close(self):
        """关闭客户端"""
        self.client.close()


# ============ 命令处理 ============

def show_help():
    """显示帮助信息"""
    help_text = """
🤖 vLLM 智能对话系统 - 命令帮助

基本命令:
  /help           显示此帮助信息
  /quit, /exit    退出程序
  /clear          清空对话历史
  /history        显示完整对话历史

历史管理:
  /save [文件名]  保存对话到文件（默认自动命名）
  /load <文件名>  加载对话历史
  /list           列出已保存的对话

配置管理:
  /config                     查看当前配置
  /config <参数> <值>         修改配置参数
  /stream                     切换流式输出模式

可配置参数:
  max_tokens      最大生成token数 (默认: 512)
  temperature     温度参数 0-2 (默认: 0.7)
  top_p           top_p采样 0-1 (默认: 0.95)
  stream          流式输出 true/false (默认: false)

示例:
  /config max_tokens 1000     设置最大token数为1000
  /config temperature 0.5     设置温度为0.5
  /save my_chat.json          保存对话
  /load my_chat.json          加载对话

使用技巧:
  • 直接输入文本即可开始对话
  • 支持多轮对话，自动维护上下文
  • 使用 Ctrl+C 可以中断当前输出
  • 流式输出需要 OpenAI 后端支持
"""
    print_colored(help_text, Colors.CYAN)


def show_welcome():
    """显示欢迎信息"""
    welcome = """
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║          🤖 vLLM 智能对话系统 v1.0                         ║
║                                                            ║
║  基于 vLLM 的交互式对话界面                                ║
║  支持多轮对话、历史记录、流式输出等功能                    ║
║                                                            ║
║  输入 /help 查看命令帮助                                   ║
║  输入 /quit 退出程序                                       ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
"""
    print_colored(welcome, Colors.BRIGHT_CYAN, bold=True)


def process_command(chat: SmartChat, command: str) -> bool:
    """
    处理命令
    返回 True 表示继续运行，False 表示退出
    """
    parts = command.strip().split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    
    if cmd in ['/quit', '/exit', '/q']:
        print_colored("\n👋 再见！", Colors.BRIGHT_YELLOW, bold=True)
        return False
    
    elif cmd == '/help':
        show_help()
    
    elif cmd == '/clear':
        chat.clear_history()
    
    elif cmd == '/history':
        chat.show_history()
    
    elif cmd == '/save':
        filename = args if args else None
        chat.save_history(filename)
    
    elif cmd == '/load':
        if not args:
            print_colored("❌ 请指定文件名: /load <文件名>", Colors.RED)
        else:
            chat.load_history(args)
    
    elif cmd == '/list':
        chat.list_saved_chats()
    
    elif cmd == '/config':
        if not args:
            chat.show_config()
        else:
            config_parts = args.split(maxsplit=1)
            if len(config_parts) != 2:
                print_colored("❌ 用法: /config <参数> <值>", Colors.RED)
            else:
                key, value = config_parts
                chat.update_config(key, value)
    
    elif cmd == '/stream':
        current = chat.config['stream']
        chat.config['stream'] = not current
        status = "开启" if chat.config['stream'] else "关闭"
        print_colored(f"✅ 流式输出已{status}", Colors.GREEN)
        
        if chat.config['stream'] and chat.config['backend'] != 'openai':
            print_colored("⚠️  警告: 流式输出需要 OpenAI 后端", Colors.YELLOW)
    
    else:
        print_colored(f"❌ 未知命令: {cmd}", Colors.RED)
        print_colored("💡 输入 /help 查看可用命令", Colors.YELLOW)
    
    return True


# ============ 主程序 ============

def main():
    """主函数"""
    show_welcome()
    
    # 初始化对话管理器
    try:
        print_colored("🔄 正在连接 vLLM 服务...", Colors.YELLOW)
        chat = SmartChat(
            base_url="http://localhost:9000",
            api_key="muyu",
            model="Medical_Qwen3_8B_Large_Language_Model",
            backend='openai'  # 使用 openai 后端支持流式输出
        )
        
        # 测试连接
        models = chat.client.get_models()
        print_colored(f"✅ 连接成功！当前模型: {models[0]}", Colors.GREEN)
        print_colored("💬 流式输出: 已开启", Colors.GREEN)
        print_colored("─" * 60 + "\n", Colors.CYAN)
        
    except Exception as e:
        print_colored(f"\n❌ 连接失败: {e}", Colors.RED)
        print_colored("\n请确保:", Colors.YELLOW)
        print_colored("  1. vLLM 服务已启动", Colors.YELLOW)
        print_colored("  2. SSH 隧道已建立（如需要）", Colors.YELLOW)
        print_colored("  3. 端口 9000 可访问", Colors.YELLOW)
        return
    
    # 主循环
    try:
        while True:
            # 获取用户输入
            try:
                user_input = input(f"{Colors.BRIGHT_BLUE}👤 你: {Colors.RESET}").strip()
            except EOFError:
                print()
                break
            
            if not user_input:
                continue
            
            # 处理命令
            if user_input.startswith('/'):
                if not process_command(chat, user_input):
                    break
                continue
            
            # 普通对话
            try:
                if chat.config['stream'] and chat.config['backend'] == 'openai':
                    # 流式输出已在 chat 方法中处理
                    chat.chat(user_input)
                else:
                    # 非流式输出
                    response = chat.chat(user_input)
                    if response:
                        print_colored("\n🤖 助手: ", Colors.BRIGHT_GREEN, bold=True)
                        print(f"{response}\n")
            
            except KeyboardInterrupt:
                print_colored("\n\n⚠️  已中断", Colors.YELLOW)
                continue
    
    except KeyboardInterrupt:
        print_colored("\n\n👋 程序已中断", Colors.BRIGHT_YELLOW)
    
    finally:
        # 清理资源
        chat.close()
        print_colored("\n✅ 资源已释放", Colors.GREEN)


if __name__ == "__main__":
    main()

