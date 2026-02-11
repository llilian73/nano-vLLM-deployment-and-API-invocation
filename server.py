import os
from flask import Flask, request, jsonify
from unittest.mock import patch
from nanovllm import LLM, SamplingParams
from transformers import AutoTokenizer, AutoConfig

# 初始化 Flask 应用
app = Flask(__name__)

# 全局变量，用于存放加载后的模型和分词器
llm_engine = None
tokenizer = None
sampling_params = None


def load_model():
    """
    加载模型和分词器。
    包含之前的热补丁逻辑，解决 Qwen3 配置字典哈希错误的问题。
    """
    global llm_engine, tokenizer, sampling_params

    # 设定模型路径
    path = os.path.expanduser("~/huggingface/Qwen3-0.6B/")

    print(f"正在准备加载模型: {path}")

    # --- 修复逻辑开始 (同 example.py) ---
    # 1. 手动加载配置到内存
    config = AutoConfig.from_pretrained(path, trust_remote_code=True)

    # 2. 临时置空 rope_scaling 避免哈希错误
    if hasattr(config, 'rope_scaling'):
        print(f"应用热补丁: 将 rope_scaling ({config.rope_scaling}) 临时置空...")
        config.rope_scaling = None

    # 3. 定义拦截函数
    original_from_pretrained = AutoConfig.from_pretrained

    def patched_from_pretrained(pretrained_model_name_or_path, *args, **kwargs):
        if pretrained_model_name_or_path == path:
            return config
        return original_from_pretrained(pretrained_model_name_or_path, *args, **kwargs)

    # 4. 在 patch 上下文中初始化 LLM
    print("正在初始化 LLM 引擎...")
    with patch("transformers.AutoConfig.from_pretrained", side_effect=patched_from_pretrained):
        llm_engine = LLM(path, enforce_eager=True, tensor_parallel_size=1)
    # --- 修复逻辑结束 ---

    # 加载分词器
    tokenizer = AutoTokenizer.from_pretrained(path)

    # 设置默认采样参数 (你可以根据需求调整 temperature)
    sampling_params = SamplingParams(temperature=0.6, max_tokens=512)
    print("模型加载完成，服务准备就绪！")


@app.route('/chat', methods=['POST'])
def chat():
    """
    RESTful API 接口
    接收 JSON: {"prompt": "你好"}
    返回 JSON: {"response": "你好！我是..."}
    """
    if not llm_engine:
        return jsonify({"error": "Model not initialized"}), 500

    # 1. 解析请求数据
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Missing 'prompt' field"}), 400

    user_input = data['prompt']
    print(f"收到请求: {user_input}")

    # 2. 应用聊天模板 (Chat Template)
    # 将用户的自然语言构造成模型能听懂的对话格式
    full_prompt = tokenizer.apply_chat_template(
        [{"role": "user", "content": user_input}],
        tokenize=False,
        add_generation_prompt=True,
    )

    # 3. 执行推理
    # generate 接受列表，所以要把 prompt 放进列表里
    outputs = llm_engine.generate([full_prompt], sampling_params)

    # 4. 提取结果
    # outputs[0] 对应输入的第一个提示词
    generated_text = outputs[0]['text']

    # 5. 返回 JSON 结果
    return jsonify({
        "status": "success",
        "input": user_input,
        "response": generated_text
    })


if __name__ == '__main__':
    # 启动前先加载模型
    load_model()
    # 启动 Flask 服务，host='0.0.0.0' 允许外部访问，端口 8000
    app.run(host='0.0.0.0', port=6006)
