# 架构治理系统培训指南

## 概述

本培训指南旨在帮助开发团队理解和使用新的架构治理系统，确保代码实现与架构文档保持一致，防止架构违规。

## 为什么需要架构治理？

### 问题背景
1. **架构文档权威性不足**：开发人员不遵循文档，自行实现
2. **架构与实际实现脱节**：架构师"编故事"，文档不匹配代码
3. **重复违规**：相同架构问题反复出现
4. **技术债务积累**：不一致的实现导致维护成本增加

### 解决方案
建立系统化的架构治理机制：
- **权威文档**：ADR作为唯一决策来源
- **自动化检查**：代码提交前自动验证架构合规性
- **明确流程**：架构变更需要正式审批
- **持续监控**：CI/CD集成架构检查

## 核心组件

### 1. 架构决策记录 (ADR) 系统

#### 什么是ADR？
- **Architectural Decision Record**：架构决策记录
- 记录重要的架构决策及其理由
- 作为团队共识和后续参考

#### ADR目录结构
```
docs/architecture/decisions/
├── ADR_TEMPLATE.md          # ADR模板
├── ADR-001-memory-index-pipeline-design.md  # 示例：记忆系统设计
├── INDEX.md                 # ADR索引
└── README.md                # 使用指南
```

#### 如何创建ADR？
1. 复制 `ADR_TEMPLATE.md`
2. 填写决策内容
3. 提交给架构评审委员会 (ARC) 审批
4. 添加到 `INDEX.md`

#### 现有ADR示例
- **ADR-001**: 记忆索引管道设计 - SQLite队列+溢出触发 vs 定期索引
  - 状态：已接受
  - 决策：使用SQLite队列+溢出触发，删除定期索引管道

### 2. 架构合规检查工具

#### 检查工具位置
```
scripts/architecture/check_document_consistency.py
```

#### 检查内容
1. **ADR合规性**：代码是否遵循ADR决策
2. **架构规则**：是否符合通用架构标准
3. **文档一致性**：实现是否匹配文档

#### 运行检查
```bash
# 检查所有架构规则
python scripts/architecture/check_document_consistency.py

# 检查特定ADR
python scripts/architecture/check_document_consistency.py --adr ADR-001

# JSON格式输出
python scripts/architecture/check_document_consistency.py --format json
```

### 3. 预提交钩子 (Pre-commit Hooks)

#### 自动检查
每次代码提交前自动运行架构检查：
```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: architecture-consistency-check
      name: 架构文档一致性检查
      entry: python scripts/architecture/check_document_consistency.py
      language: system
      types: [python]
      pass_filenames: false
      always_run: true
      verbose: true
```

#### 检查逻辑
1. 检测架构相关文件变更
2. 运行架构一致性检查
3. 如果失败，阻止提交
4. 提供详细错误信息和修复建议

### 4. CI/CD集成

#### GitHub Actions工作流
```yaml
# .github/workflows/ci.yml
architecture-compliance:
  name: Architecture Compliance Check
  runs-on: ubuntu-latest
  
  steps:
    - uses: actions/checkout@v4
    - name: Run architecture compliance check
      run: python scripts/architecture/check_document_consistency.py --format text
```

#### 检查结果
- 通过：继续后续测试
- 失败：停止流水线，需要修复架构问题

### 5. 架构评审委员会 (ARC)

#### 委员会职责
- 评审和批准ADR
- 监督架构合规性
- 处理架构违规
- 提供架构指导

#### 会议安排
- **每周评审**：周一10:00 AM (30分钟)
- **月度深度评审**：每月第一个周三 (2小时)
- **紧急会议**：按需召开

## 开发工作流程

### 1. 日常开发

#### 提交代码前
```bash
# 1. 运行架构检查
python scripts/architecture/check_document_consistency.py

# 2. 如果失败，查看报告并修复
# 3. 重新运行检查直到通过
# 4. 提交代码
```

#### 遇到架构问题
1. 查看相关ADR文档
2. 如果ADR不明确，提交问题
3. 如果需要变更架构，创建新ADR提案

### 2. 架构变更流程

#### 小变更（不影响ADR）
1. 确保代码符合现有ADR
2. 提交代码，通过预提交检查
3. 代码审查通过后合并

#### 大变更（需要新ADR）
1. **提案阶段**：创建ADR草案
2. **评审阶段**：提交给ARC评审
3. **决策阶段**：ARC投票决定
4. **实施阶段**：按照ADR实现
5. **验证阶段**：确保实现符合ADR

### 3. 处理架构违规

#### 发现违规
1. 预提交钩子或CI/CD检查失败
2. 查看详细错误信息
3. 确定违规类型

#### 违规类型
- **ADR违规**：违反已接受的ADR决策
- **架构规则违规**：违反通用架构标准
- **文档不一致**：代码与文档不匹配

#### 修复步骤
1. **理解违规**：阅读相关ADR和错误信息
2. **分析原因**：为什么会出现违规
3. **制定方案**：如何修复
4. **实施修复**：修改代码或文档
5. **验证修复**：重新运行检查

## 实际案例：记忆系统

### 问题背景
- 记忆系统有多个实现版本
- 定期索引管道与SQLite队列设计冲突
- 开发人员不清楚应该遵循哪个设计

### ADR决策
- **ADR-001**：选择SQLite队列+溢出触发索引
- **否决**：定期索引管道方案
- **要求**：删除memory_index_pipeline.py

### 实施步骤
1. **清理代码**：删除memory_index_pipeline.py
2. **更新调度器**：移除索引任务
3. **更新文档**：反映最新设计
4. **设置检查**：确保不再出现定期索引

### 检查规则
```python
# ADR-001相关检查规则
ArchitectureRule(
    rule_id="ADR-001-05",
    description="不应存在定期索引管道文件",
    pattern=r"memory_index_pipeline",
    required=False,  # 应该不存在
    files=["**/memory_index_pipeline.py"],
    adr_reference="ADR-001",
),
```

## 最佳实践

### 1. 文档优先
- 先写文档，再写代码
- 文档作为实现的蓝图
- 保持文档与代码同步

### 2. 遵守ADR
- ADR是架构决策的唯一来源
- 不理解ADR时先询问
- 不随意偏离ADR决策

### 3. 主动检查
- 开发过程中定期运行架构检查
- 不要等到提交时才发现问题
- 使用IDE插件或脚本自动化检查

### 4. 及时反馈
- 发现ADR问题及时报告
- 提出改进建议
- 参与架构讨论

### 5. 持续学习
- 定期阅读ADR文档
- 参加架构培训
- 学习架构最佳实践

## 常见问题解答

### Q1: 如果我认为ADR决策有问题怎么办？
A: 可以提出修改建议，但需要：
1. 创建ADR修改提案
2. 提交给ARC评审
3. 获得批准后才能修改

### Q2: 紧急修复时架构检查失败怎么办？
A: 可以申请临时例外：
1. 提交例外申请
2. ARC快速评审
3. 获得批准后添加例外注释
4. 后续必须修复架构问题

### Q3: 如何添加新的架构规则？
A: 通过以下步骤：
1. 确定规则范围和必要性
2. 创建规则定义
3. 添加到检查工具
4. 更新文档
5. 通知团队

### Q4: 架构检查影响开发效率怎么办？
A: 架构检查的目的是：
- 预防问题，减少后期修复成本
- 确保代码质量，降低维护成本
- 提高团队协作效率

## 资源链接

### 文档
- [ADR系统指南](/docs/architecture/decisions/README.md)
- [架构治理策略](/docs/architecture/governance-policy.md)
- [ARC委员会章程](/docs/architecture/architecture-review-committee.md)
- [所有ADR列表](/docs/architecture/decisions/INDEX.md)

### 工具
- [架构检查工具](/scripts/architecture/check_document_consistency.py)
- [预提交钩子配置](/.pre-commit-config.yaml)
- [CI/CD配置](/.github/workflows/ci.yml)

### 联系方式
- **架构评审委员会**：architecture-review@fitmind.example.com
- **Slack频道**：#architecture-review
- **紧急联系人**：[技术负责人姓名]

## 培训考核

### 知识测试
1. ADR是什么？有什么作用？
2. 如何运行架构检查？
3. 发现架构违规如何处理？
4. 需要变更架构时应该怎么做？

### 实践任务
1. 运行架构检查并理解报告
2. 查看ADR-001并理解记忆系统设计
3. 尝试修改代码触发架构违规
4. 修复架构违规并通过检查

### 认证要求
- 完成知识测试（80%以上正确）
- 完成实践任务
- 理解并承诺遵守架构治理政策

---

*培训版本：1.0*  
*更新日期：2026-02-27*  
*培训对象：所有开发人员*  
*培训时长：2小时（理论+实践）*

## 附录

### A. 快速参考卡片

#### 常用命令
```bash
# 架构检查
python scripts/architecture/check_document_consistency.py

# 检查特定ADR
python scripts/architecture/check_document_consistency.py --adr ADR-001

# 安装预提交钩子
pre-commit install

# 手动运行预提交检查
pre-commit run --all-files
```

#### 关键文件
- `docs/architecture/decisions/` - ADR文档
- `scripts/architecture/check_document_consistency.py` - 检查工具
- `.pre-commit-config.yaml` - 预提交配置
- `.github/workflows/ci.yml` - CI/CD配置

#### 重要规则
- 所有架构变更必须有ADR
- 代码必须通过架构检查
- 文档必须与代码一致
- 架构违规必须及时修复

### B. 故障排除

#### 预提交钩子失败
```bash
# 查看详细错误
pre-commit run architecture-consistency-check --verbose

# 跳过检查（仅用于调试）
git commit --no-verify -m "message"
```

#### 架构检查误报
1. 检查规则定义是否正确
2. 确认代码确实符合架构
3. 如果是误报，更新检查规则
4. 重新运行检查

#### CI/CD检查失败
1. 查看GitHub Actions日志
2. 下载架构检查报告
3. 本地复现问题
4. 修复后重新推送

### C. 进阶学习

#### 推荐阅读
- [架构决策记录模式](https://adr.github.io/)
- [文档驱动开发](https://documentation-driven-development.info/)
- [架构治理最佳实践](https://martinfowler.com/architecture/)

#### 内部资源
- 架构设计模式文档
- 代码审查指南
- 技术债务管理策略

#### 培训材料
- 架构设计工作坊
- 代码质量培训
- 技术领导力发展