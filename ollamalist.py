import tkinter as tk
from tkinter import ttk, messagebox
import requests
from threading import Thread
import sys
import os

class OllamaModelViewer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Ollama 模型查看器")
        self.root.geometry("600x400")
        
        # 添加图标（如果有的话）
        try:
            if getattr(sys, 'frozen', False):
                application_path = sys._MEIPASS
            else:
                application_path = os.path.dirname(os.path.abspath(__file__))
            self.root.iconbitmap(os.path.join(application_path, 'icon.ico'))
        except:
            pass
            
        self.setup_ui()
        
    def setup_ui(self):
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建树形视图
        columns = ('名称', '大小', '修改时间')
        self.tree = ttk.Treeview(self.main_frame, columns=columns, show='headings')
        
        # 设置列标题
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 放置组件
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 添加刷新按钮
        self.refresh_btn = ttk.Button(self.root, text="刷新列表", command=self.refresh_models)
        self.refresh_btn.pack(pady=10)
        
        # 加载模型列表
        self.refresh_models()

    def load_models(self):
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)  # 添加超时设置
            if response.status_code == 200:
                models = response.json().get('models', [])
                if not models:
                    self.tree.insert('', tk.END, values=('未找到已安装的模型', '', ''))
                    return
                    
                for model in models:
                    self.tree.insert('', tk.END, values=(
                        model.get('name', 'Unknown'),
                        model.get('size', 'Unknown'),
                        model.get('modified', 'Unknown')
                    ))
            else:
                self.tree.insert('', tk.END, values=('获取模型列表失败', '', ''))
                messagebox.showerror("错误", "无法连接到 Ollama 服务")
        except requests.exceptions.ConnectionError:
            self.tree.insert('', tk.END, values=('无法连接到 Ollama 服务', '', ''))
            messagebox.showerror("错误", "无法连接到 Ollama 服务，请确保 Ollama 正在运行")
        except Exception as e:
            self.tree.insert('', tk.END, values=(f'错误: {str(e)}', '', ''))
            messagebox.showerror("错误", f"发生错误：{str(e)}")
        finally:
            self.root.after(0, lambda: self.refresh_btn.configure(state='normal'))
    def refresh_models(self):
        self.refresh_btn.configure(state='disabled')
        # 清空现有项目
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        Thread(target=self.load_models).start()
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = OllamaModelViewer()
    app.run()
