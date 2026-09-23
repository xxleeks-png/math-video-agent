# Math Video Agent

小学数学讲题视频 AI Agent。

## v0.1.0

第一阶段目标：先建立“题目 -> 结构化解题结果”的最小闭环，暂不生成视频。

### 当前能力

- FastAPI 健康检查
- 一个经过验证的水池流水问题
- Pydantic 结构化输出
- pytest 自动测试

### 本地运行

~~~bash
python -m venv .venv
# Windows PowerShell
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
pytest
uvicorn backend.main:app --reload
~~~

打开 http://127.0.0.1:8000/docs 测试 API。

## 下一步

1. 接入 LLM 做题目解析
2. 将题目转换成统一 Problem JSON
3. 增加数学验证器
4. 生成小学老师口吻的多版本讲解
5. 建立 Video DSL
6. 接入 TTS、字幕和 Manim/FFmpeg 渲染
