# 🤝 贡献指南 / Contributing

感谢你有兴趣为 video-to-brain 做贡献！

这个项目是一个零编程基础的人用 vibe coding 做出来的。如果你也是非程序员，别担心，这里欢迎所有人。

---

## 🎯 可以做什么

### 不需要写代码
- 🐛 **报 Bug** — 用的时候出错了？[提个 Issue](https://github.com/LunaAI519/video-to-brain/issues/new?template=bug_report.md)
- 💡 **提建议** — 想到新功能？[提个 Feature Request](https://github.com/LunaAI519/video-to-brain/issues/new?template=feature_request.md)
- 📖 **改文档** — 觉得哪里说得不清楚？直接改
- 🌍 **翻译** — 帮忙翻译成其他语言
- ⭐ **给个 Star** — 最简单的支持方式

### 需要写代码
- 🔧 修复 Bug
- ✨ 新增笔记模板
- 🧪 添加测试
- 🚀 性能优化

---

## 📋 提交代码流程

1. **Fork** 这个仓库
2. **创建分支**: `git checkout -b feature/你要做的事`
3. **写代码**
4. **测试**: `python -m pytest tests/`
5. **提交**: `git commit -m "feat: 描述你做了什么"`
6. **推送**: `git push origin feature/你要做的事`
7. **提 PR**: 到 GitHub 页面提交 Pull Request

### Commit 规范

```
feat: 新功能
fix: 修复 Bug
docs: 文档更新
test: 添加测试
refactor: 代码重构（不改功能）
```

---

## 🏗️ 开发环境

```bash
git clone https://github.com/你的用户名/video-to-brain.git
cd video-to-brain
pip install -r requirements.txt
pip install pytest  # 测试

# 跑测试
python -m pytest tests/ -v
```

---

## 📝 笔记模板贡献

想增加新的笔记模板？修改 `src/ai_processor.py`：

1. 在 `TEMPLATES` 字典里添加新模板
2. 写好 `prompt`（告诉 AI 输出什么格式的 JSON）
3. 在 `src/note_generator.py` 里添加对应的渲染逻辑
4. 提 PR

---

## ❓ 不确定？

直接 [开个 Issue](https://github.com/LunaAI519/video-to-brain/issues) 问就行。没有蠢问题。

---

感谢每一个贡献者 ❤️
