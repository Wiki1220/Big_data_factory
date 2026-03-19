# API Contract

本文件定义自动化脚本对 AI 暴露的动作契约。AI 只应读取本文件或等价的结构化输出，不应阅读脚本源码。

## 原则

- 脚本按 API 使用，不按源码使用。
- 输入参数必须显式。
- 输出必须结构化。
- 错误必须可归类。
- 同一动作连续失败 `3` 次后进入手动模式。

## 通用输入

每个动作至少接受以下公共参数：

- `job_id`
- `build_id`
- `spec_path`
- `builder`
- `node_selector`
- `timeout_sec`
- `retry_limit`
- `manual_mode_after`

默认值：

- `retry_limit=3`
- `manual_mode_after=3`

## 通用输出

所有动作都应输出 JSON，至少包含：

- `action`
- `status`
- `job_id`
- `build_id`
- `attempt`
- `manual_mode`
- `message`
- `artifacts`
- `next_actions`
- `error_code`

`status` 取值：

- `success`
- `failed`
- `manual_mode`

## 动作列表

### check_host_env

用途：

- 校验宿主机环境、虚拟化能力、路径和必要依赖。

额外输入：

- `require_vmware`
- `require_disk_gb`
- `require_memory_mb`

成功输出：

- 宿主机检查结果
- 缺失项列表
- 建议下一步动作

### bootstrap_vm

用途：

- 创建虚拟机、设置基础资源、等待开机可达。

额外输入：

- `base_image`
- `vm_hardware_version`
- `cpu`
- `memory_mb`
- `disk_gb`
- `network_name`

成功输出：

- 已创建节点列表
- 节点 IP
- SSH 可达状态

### push_packages

用途：

- 将离线软件包分发到目标节点。

额外输入：

- `package_set`
- `destination_dir`
- `checksum_verify`

### render_and_apply_configs

用途：

- 渲染模板并注入节点。

额外输入：

- `template_group`
- `variables_file`
- `service_name`

### validate_cluster

用途：

- 执行节点连通、服务健康和样例作业验证。

额外输入：

- `checks`
- `stop_on_first_failure`

### export_artifact

用途：

- 导出镜像、生成校验信息和交付清单。

额外输入：

- `export_format`
- `output_dir`
- `include_docs`

## 手动模式

当同一动作连续失败达到 `manual_mode_after` 次时：

- 当前动作返回 `status=manual_mode`
- `manual_mode=true`
- `next_actions` 不再包含自动重试
- 响应必须附带最近失败原因摘要

此时 AI 只能：

- 向用户报告阻塞原因
- 请求人工介入
- 在人工处理后重新开始新的动作调用
