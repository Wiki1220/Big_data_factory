# Big Data Factory

`Big Data Factory` 是一个用于生产大数据虚拟机镜像的自动化工厂。它的目标不是手工维护一批虚拟机目录，而是基于声明式规格，稳定地生成可交付、可追溯、可验证的集群镜像产物。

## AI Entry

本节是给 AI 的入口提示。AI 首先读取本节，再按需读取后续章节，避免一次性加载整份文档。

### 你的角色

你是这个工厂的控制面操作员。你的职责是把需求收敛成规格，驱动标准流水线，并输出可追溯的交付物。你不是手工改虚拟机的人。

### 你的目标

- 把客户需求收敛为 `specs/clusters/*.yaml`
- 基于 `spec` 生成构建计划
- 按流水线阶段推进任务
- 记录状态、产物和关键决策
- 只交付经过验证的镜像

### 你必须遵守的规则

- 以 `spec` 作为唯一需求入口，不要绕过规格直接改镜像。
- 只通过标准流水线推进任务，不要跳过 `plan -> build -> verify -> export -> publish`。
- 不要手工改数据库，不要手工伪造 manifest。
- 如果输入需求不完整，先补齐规格，再进入构建。
- 输出给用户的是结果摘要，不是内部长日志。
- 默认只把 `工厂服务器` 作为远端操作面，不要把每台 VM 当成 AI 的直接主操作对象。

### 你当前应优先读取的对象

1. 当前任务对应的 `spec`
2. 当前任务状态摘要
3. 当前允许执行的下一步动作
4. 相关模板或执行器说明

不要默认读取所有历史任务、所有日志和所有模板。

### 最小工作流

1. 读取或生成 `spec`
2. 校验目标平台、节点拓扑、软件版本、网络配置
3. 生成 `plan`
4. 调用对应 `builder`
5. 执行验证
6. 生成交付物和 manifest
7. 输出简明结果摘要

### 失败处理原则

- 优先报告阻塞原因，不要隐式兜底。
- 不要擅自改变客户需求来规避失败。
- 如果是依赖缺失、环境不满足或规格冲突，明确指出缺口。
- 失败后保留中间状态，便于重试和审计。

## 1. 目标

本项目解决以下问题：

- 统一接收不同客户的大数据环境需求。
- 复用离线软件仓库和配置模板，降低重复下载和重复配置成本。
- 按规格自动构建多节点虚拟机集群。
- 对产物执行启动、联通、服务和样例作业验证。
- 将最终镜像导出为标准交付物，并记录完整生命周期。

当前版本先聚焦生产级最小可行工厂：

- 输入：声明式需求规格文件。
- 过程：构建计划、模板渲染、生命周期记录。
- 输出：构建目录、生命周期数据库、后续执行入口。

## 2. 设计原则

- 第一性原理：系统的源头是 `spec`，不是某个手工修改过的虚拟机。
- 单一事实来源：软件版本、节点拓扑、网络规划、导出目标都来自规格文件。
- 可追溯：任何交付物都必须能反查到输入规格、软件版本、模板版本和构建结果。
- 幂等：同一份规格重复构建，行为必须可预期。
- 最短路径：先支持 VMware 作为构建执行器，后续再扩展其他虚拟化目标。
- 控制面与执行面分离：AI 和脚本只负责控制面，真正创建/导出虚拟机由执行器负责。

## 3. 总体架构

系统分为 6 层：

1. `specs`
   定义客户需求和目标集群拓扑。
2. `eco-store`
   存储离线软件包和中间件分发文件。
3. `templates`
   存储配置模板、云初始化模板和脚本模板。
4. `pipeline`
   负责编排生命周期：读取规格、生成计划、分发任务、记录结果。
5. `builders`
   对接虚拟化平台，执行虚拟机创建、配置注入、启动验证和导出。
6. `artifacts/manifests/state`
   保存产物、元数据和生命周期状态。

```text
spec -> plan -> build -> verify -> export -> publish
```

## 4. 目录结构

```text
Big_data_factory/
  README.md
  pyproject.toml
  .gitignore
  docs/
    architecture.md
  specs/
    clusters/
      hadoop-3node.yaml
  templates/
    services/
      hadoop/
        core-site.xml.j2
        hdfs-site.xml.j2
  eco-store/
    README.md
  base-images/
    README.md
  manifests/
    README.md
  artifacts/
    .gitkeep
  state/
    .gitkeep
    schema.sql
  tests/
    README.md
  src/
    big_data_factory/
      __init__.py
      cli.py
      config.py
      models.py
      planner.py
      state.py
      utils.py
      pipeline/
        __init__.py
      builders/
        __init__.py
        vmware.py
```

目录职责：

- `specs/clusters/`：客户需求或标准环境规格。
- `templates/services/`：服务配置模板。
- `eco-store/`：离线生态仓库，按软件类别组织内容。
- `base-images/`：基础操作系统镜像和基础模板来源说明。
- `manifests/`：构建元数据及产物清单存放位置。
- `artifacts/`：最终镜像、校验文件、交付清单。
- `state/`：轻量级生命周期数据库和运行态文件。
- `src/big_data_factory/`：控制面代码。

## 5. 生命周期模型

每次构建都对应一条 `build` 生命周期记录。

标准阶段定义：

1. `requested`
   接收到规格，等待生成计划。
2. `planned`
   规格通过校验，已经生成执行计划。
3. `building`
   执行器正在创建虚拟机和注入内容。
4. `verifying`
   正在执行节点与集群验证。
5. `exporting`
   正在导出镜像和交付文件。
6. `published`
   产物已落盘或已上传对象存储。
7. `failed`
   任一阶段失败。

## 6. 规格文件设计

规格文件位于 `specs/clusters/`。它是系统唯一的需求入口。

示例字段：

- `metadata`
  规格标识、版本、作者、说明。
- `target`
  目标虚拟化平台和导出格式。
- `cluster`
  集群名称、环境、节点集合。
- `software`
  软件版本矩阵。
- `network`
  网络规划和 DNS/网关信息。
- `validation`
  本次交付必须执行的验证动作。

样例见 [hadoop-3node.yaml](/Users/regen-bio/CODE/Big_data_factory/specs/clusters/hadoop-3node.yaml)。

## 7. 生命周期数据库

当前使用轻量级 `SQLite` 记录生命周期。这样做的原因：

- 够轻，不引入额外运维负担。
- 支持本地单机工厂的状态记录。
- 后续如果要切到 MySQL/PostgreSQL，只需替换状态存储层。

数据库核心表：

- `builds`
  记录一次构建的主状态。
- `build_events`
  记录阶段推进和异常详情。
- `artifacts`
  记录交付物路径、hash、格式和兼容目标。

Schema 见 [schema.sql](/Users/regen-bio/CODE/Big_data_factory/state/schema.sql)。

## 8. 执行模型

当前代码先提供控制面骨架，不直接创建虚拟机。执行过程分为两步：

1. 读取规格并生成构建计划。
2. 将计划交给具体构建执行器。

初版执行器为 `vmware`：

- 负责 VMware 虚拟机的创建、配置注入、启动和导出。
- 当前以接口骨架形式保留，后续接入实际命令和模板流程。

## 8.1 推荐部署拓扑

推荐把系统部署成三层，而不是让 AI 直接管理所有虚拟机：

1. `本地 AI`
   负责读取需求、生成规格、触发工厂命令、查看任务摘要。
2. `Linux 工厂服务器`
   负责运行控制面、状态库、模板渲染、构建执行器和产物管理。
3. `目标 VM 网络`
   由工厂服务器统一创建、初始化、验证和导出。

推荐链路：

```text
AI workstation -> SSH -> factory server -> SSH -> target VMs
```

但对 AI 来说，唯一直接连接的远端应当只有 `factory server`。

## 8.2 SSH 边界原则

两层 SSH 本身不是问题，问题在于职责边界是否清晰。

正确边界：

- `AI -> 工厂服务器`
  只执行工厂标准命令。
- `工厂服务器 -> VM`
  由 builder 或验证器负责节点初始化、配置注入和验证。

不推荐的主流程：

- AI 先 SSH 到服务器，再手工 SSH 到每一台 VM 执行零散命令。

原因：

- 容易让 AI 丢失当前所在机器的上下文。
- VM 级凭据会扩散到 AI 侧。
- 审计日志分散，难以复盘。
- 临时命令不易沉淀为标准流水线。

因此，系统默认规则应为：

- AI 只操作工厂服务器。
- 工厂服务器统一持有或调度 VM 访问凭据。
- VM 只作为 builder 的受控资源，不作为 AI 的默认直接操作面。

## 8.3 服务器侧职责

工厂服务器至少承担以下职责：

- 保存 `specs`、`templates`、`eco-store`
- 运行生命周期数据库
- 驱动构建执行器
- 统一管理到 VM 的 SSH 连接
- 收集验证结果和交付物

这意味着服务器操作系统优先选择 `Linux`，而不是 `Windows`。

## 9. 使用方式

### 9.1 环境要求

- Python `3.11+`
- 本地文件系统可写
- 后续如启用 VMware 构建，需要宿主机安装 VMware Workstation Pro

### 9.2 安装

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 9.3 初始化状态库

```bash
python -m big_data_factory.cli init-state
```

执行后将在 [state/factory.db](/Users/regen-bio/CODE/Big_data_factory/state/factory.db) 创建生命周期数据库。

### 9.4 读取规格并生成计划

```bash
python -m big_data_factory.cli plan --spec specs/clusters/hadoop-3node.yaml
```

输出内容：

- 本次构建的 `build_id`
- 目标执行器
- 节点数量
- 计划阶段列表

### 9.5 后续扩展命令

后续将补齐如下命令：

- `build`
- `verify`
- `export`
- `publish`

## 10. 交付物规范

最终交付目录建议格式：

```text
artifacts/
  <build_id>/
    manifest.json
    checksums.txt
    nodes/
      master-01.ova
      worker-01.ova
      worker-02.ova
    docs/
      import-guide.md
      topology.md
```

要求：

- 每个产物必须带 hash。
- 每次交付必须附带 manifest。
- 交付文档必须说明导入方式、默认网络、账号初始化方式和兼容范围。

## 11. AI Skill 的职责边界

AI 只负责控制面，不直接绕过规格和流水线修改虚拟机内容。

允许 AI 做的事：

- 解析客户需求并生成规格草案。
- 选择软件版本矩阵。
- 渲染模板参数。
- 驱动标准流水线命令。
- 汇总验证结果与交付说明。

不允许 AI 直接做的事：

- 无规格直接改镜像。
- 跳过校验阶段直接交付。
- 手工修改运行态数据库。
- 绕过 manifest 发布不透明产物。

## 12. 开发顺序建议

第一阶段：

- 固化规格 schema。
- 接入真实 VMware 构建器。
- 增加模板渲染能力。
- 增加状态推进和事件记录。

第二阶段：

- 增加验证器。
- 增加交付打包和 checksum。
- 增加对象存储发布。

第三阶段：

- 增加 KVM/QCOW2 等其他目标导出器。
- 增加 Web/API 控制面。
- 增加多并发构建调度。

## 13. 当前状态

当前仓库已经完成：

- 工程目录搭建
- Python 包骨架
- 生命周期状态库 schema
- 样例规格文件
- 计划阶段入口命令
- 项目设计与使用说明

未完成：

- 真实虚拟机构建
- 模板渲染落盘
- 服务安装与集群验证
- 镜像导出与对象存储发布

这部分会在后续迭代中逐步接入。
