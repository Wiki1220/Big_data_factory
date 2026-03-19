# Architecture

本文件用于承接 `README` 中的总体设计，后续扩展更细的执行器设计、模板系统设计和交付契约。

当前系统分为三部分：

- 控制面：`src/big_data_factory/`
- 生命周期状态：`state/`
- 构建与交付产物：`artifacts/`

推荐部署为三层：

- 本地 AI：只负责需求收敛和触发工厂动作
- Linux 工厂服务器：负责控制面、状态库和执行器
- 目标 VM 网络：由服务器统一管理和验证

推荐 SSH 责任链：

```text
AI workstation -> factory server -> target VMs
```

设计原则：

- AI 默认只连接工厂服务器
- 服务器统一连接和管理目标 VM
- VM 不作为 AI 的主操作面
- 所有 VM 级动作都应沉淀到 builder 或 verifier 中

后续演进方向：

- 增加规格校验 schema
- 增加模板渲染器
- 增加真实构建执行器
- 增加验证器与导出器
