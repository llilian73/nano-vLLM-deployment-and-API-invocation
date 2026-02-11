Nano-vllm + Flask：从零搭建 AI 推理服务指南
本教程将指导你在 AutoDL 等 Linux 服务器上，基于 nano-vllm 部署一个 Qwen3 模型，并通过 HTTP 接口供外部调用。

第一步：环境准备

安装必要依赖 在终端执行以下命令安装 Flask 和其他依赖：

Bash
pip clone https://github.com/GeeeekExplorer/nano-vllm.git
pip install flask transformers requests
pip install git+https://github.com/GeeeekExplorer/nano-vllm.git
hf download Qwen/Qwen3-0.6B --local-dir ~/huggingface/Qwen3-0.6B/ #下载qwen3模型
确认模型位置 确保模型文件存放在 ~/huggingface/Qwen3-0.6B/ 目录下（包含 config.json 等文件）。 如果位置不同，请记下路径，修改代码。

第二步：编写服务端代码 (server.py)
在 nano-vllm 目录下新建 server.py。 此代码包含了一个关键热补丁，用于修复 Qwen3 模型配置中 rope_scaling 字典导致的 TypeError 报错。


第三步：启动服务
在服务器终端运行：

Bash
python server.py

第四步：获取公网访问地址 (AutoDL)
回到 AutoDL 网页控制台。

找到正在运行的实例，点击 “自定义服务”（或显示为“访问 6006”的链接）。

复制弹出的长网址。

例如：https://u835453-xxxx.bjb1.seetacloud.com:8443

这就是你的公网 API 接口地址。

📱 第五步：客户端调用 (client.py)
在本地电脑（Windows/Mac）新建 client.py，代码修改成刚才获取的地址运行后即可对话。
