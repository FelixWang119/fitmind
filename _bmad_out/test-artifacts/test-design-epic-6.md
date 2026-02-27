---
stepsCompleted: []
lastStep: ''
lastSaved: ''
---

# Test Design: Epic 6 - 智能健康评估与建议系统

**Date:** 2026-02-25
**Author:** Felix
**Status:** Draft

---

## Executive Summary

**Scope:** full test design for Epic 6

**Risk Summary:**

- Total risks identified: 5
- High-priority risks (≥6): 3
- Critical categories: BUS, DATA

**Coverage Summary:**

- P0 scenarios: 3 (30 hours)
- P1 scenarios: 4 (40 hours)
- P2/P3 scenarios: 5 (25 hours)
- **Total effort**: 95 hours (~12 days)

---

## Not in Scope

| Item | Reasoning | Mitigation |
|------|-----------|------------|
| 前端页面渲染 | 已由 Epic-5 科学量化展示覆盖 | 仅测试数据绑定正确性 |
| 第三方API集成 | 待定义 | 后续添加测试 |

---

## Risk Assessment

### High-Priority Risks (Score ≥6)

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation | Owner | Timeline |
| ------- | -------- | ----------- | ----------- | ------ | ----- | ---------- | ------- | -------- |
| R-001 | BUS | 健康评分算法计算错误导致错误建议 | 2 | 3 | 6 | 单元测试覆盖所有计算场景，边界测试 | Dev Team | 2026-02-26 |
| R-002 | DATA | 评估数据可视化不准确影响用户决策 | 2 | 3 | 6 | E2E测试验证图表准确性，数据源审计 | QA Team | 2026-02-27 |
| R-003 | BUSINESS | 个性化建议生成不准确 | 3 | 2 | 6 | A/B测试验证建议有效性，用户反馈循环 | Dev Team | 2026-02-28 |

### Medium-Priority Risks (Score 3-4)

| Risk ID | Category | Description | Probability | Impact | Score | Mitigation | Owner |
| ------- | -------- | ----------- | ----------- | ------ | ----- | ---------- | ------- |
| R-004 | TECH | 健康趋势分析逻辑不一致 | 2 | 2 | 4 | 集成测试验证时间序列分析 | Dev Team |
| R-005 | PERF | 评估报告性能问题（大数据量） | 2 | 2 | 4 | 压力测试，分页优化 | Dev Team |

### Low-Priority Risks (Score 1-2)

| Risk ID | Category | Description | Probability | Impact | Score | Action |
| ------- | -------- | ----------- | ----------- | ------ | ----- | ------- |
| R-006 | OPS | 部署配置错误 | 1 | 1 | 1 | Monitor |

### Risk Category Legend

- **TECH**: Technical/Architecture (flaws, integration, scalability)
- **SEC**: Security (access controls, auth, data exposure)
- **PERF**: Performance (SLA violations, degradation, resource limits)
- **DATA**: Data Integrity (loss, corruption, inconsistency)
- **BUS**: Business Impact (UX harm, logic errors, revenue)
- **OPS**: Operations (deployment, config, monitoring)

---

## Entry Criteria

- [ ] Requirements and assumptions agreed upon by QA, Dev, PM
- [ ] Test environment provisioned and accessible
- [ ] Test data available or factories ready
- [ ] Feature deployed to test environment
- [ ] Epic 6 stories created and accepted

## Exit Criteria

- [ ] All P0 tests passing
- [ ] All P1 tests passing (or failures triaged)
- [ ] No open high-priority / high-severity bugs
- [ ] Test coverage agreed as sufficient
- [ ] Risk mitigations complete

## Project Team (Optional)

**Include only if roles/names are known or responsibility mapping is needed; otherwise omit.**

---

## Test Coverage Plan

### P0 (Critical) - Run on every commit

**Criteria**: Blocks core journey + High risk (≥6) + No workaround

| Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
| ----------- | ---------- | --------- | ---------- | ----- | ----- |
| 三维健康评估 | E2E | R-001 | 3 | QA | 核心用户旅程 |
| 健康评分计算 | Unit + E2E | R-001, R-002 | 5 | QA | 算法准确性 |
| 数据可视化 | E2E | R-002 | 3 | QA | 图表准确性 |

**Total P0**: 11 tests, 30 hours

### P1 (High) - Run on PR to main

**Criteria**: Important features + Medium risk (3-4) + Common workflows

| Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
| ----------- | ---------- | --------- | ---------- | ----- | ----- |
| 趋势分析 | API | R-004 | 4 | QA | 时间序列逻辑 |
| 个性化建议 | E2E | R-003 | 5 | QA | A/B测试支持 |

**Total P1**: 9 tests, 40 hours

### P2 (Medium) - Run nightly/weekly

**Criteria**: Secondary features + Low risk (1-2) + Edge cases

| Requirement | Test Level | Risk Link | Test Count | Owner | Notes |
| ----------- | ---------- | --------- | ---------- | ----- | ----- |
| 报告生成 | API | R-005 | 3 | QA | 性能测试 |
| 边界条件 | Unit | - | 5 | DEV | Edge cases |

**Total P2**: 8 tests, 20 hours

### P3 (Low) - Run on-demand

**Criteria**: Nice-to-have + Exploratory + Performance benchmarks

| Requirement | Test Level | Test Count | Owner | Notes |
| ----------- | ---------- | ---------- | ----- | ----- |
| 国际化支持 | Unit | 2 | DEV | Future feature |
| 离线模式 | Unit | 2 | DEV | Future feature |

**Total P3**: 4 tests, 5 hours

---

## Execution Order

### Smoke Tests (<5 min)

**Purpose**: Fast feedback, catch build-breaking issues

- [ ] 登录并进入健康评估页面 (30s)
- [ ] 完成三维健康评估 (45s)
- [ ] 查看健康评分结果 (1min)

**Total**: 3 scenarios

### P0 Tests (<10 min)

**Purpose**: Critical path validation

- [ ] 三维评估准确计算 (E2E)
- [ ] 健康评分算法边界测试 (Unit)
- [ ] 数据可视化准确性验证 (E2E)

**Total**: 3 scenarios

### P1 Tests (<30 min)

**Purpose**: Important feature coverage

- [ ] 趋势分析逻辑验证 (API)
- [ ] 个性化建议生产流程 (E2E)

**Total**: 2 scenarios

### P2/P3 Tests (<60 min)

**Purpose**: Full regression coverage

- [ ] 边界条件测试 (Unit)
- [ ] 性能压力测试 (API)

**Total**: 4 scenarios

---

## Resource Estimates

### Test Development Effort

| Priority | Count | Hours/Test | Total Hours | Notes |
| -------- | ----- | ---------- | ----------- | ----- |
| P0 | 11 | 2.0 | 30 | Complex setup, edge cases |
| P1 | 9 | 1.0 | 40 | Standard coverage |
| P2 | 8 | 0.5 | 20 | Simple scenarios |
| P3 | 4 | 0.25 | 5 | Exploratory |
| **Total** | **32** | **-** | **95** | **~12 days** |

### Prerequisites

**Test Data:**
- User factory (faker-based, auto-cleanup)
- Health assessment fixture (setup/teardown)

**Environment:**
- Postgres database with health data
- Backend API endpoints ready

---

## Quality Gate Criteria

### Pass/Fail Thresholds

- **P0 pass rate**: 100% (no exceptions)
- **P1 pass rate**: ≥95% (waivers required for failures)
- **P2/P3 pass rate**: ≥90% (informational)
- **High-risk mitigations**: 100% complete or approved waivers

### Coverage Targets

- **Critical paths**: ≥80%
- **Business logic**: ≥70%
- **Edge cases**: ≥50%

### Non-Negotiable Requirements

- [ ] All P0 tests pass
- [ ] No high-risk (≥6) items unmitigated
- [ ] Health scoring algorithm tested comprehensively

---

## Mitigation Plans

### R-001: 健康评分算法计算错误 (Score: 6)

**Mitigation Strategy:** 
- 单元测试覆盖所有计算场景，包括边界值
- E2E测试验证前端展示与后端计算一致
- 邀请营养学专家评审算法逻辑
**Owner:** Dev Team
**Timeline:** 2026-02-26
**Status:** Planned
**Verification:** Test results reviewed by QA weekly

### R-002: 评估数据可视化不准确 (Score: 6)

**Mitigation Strategy:**
- E2E测试验证图表数据绑定正确性
- 数据源审计确保数据完整性
- 手动抽查10%的可视化结果
**Owner:** QA Team
**Timeline:** 2026-02-27
**Status:** Planned
**Verification:** Audit trail documented

---

## Assumptions and Dependencies

### Assumptions

1. 健康评估算法逻辑由后端API提供，前端只负责展示
2. 用户健康数据已通过 Epic 3 (健康数据记录) 完整收集
3. 评分算法基于公开的营养学和运动医学标准
4. 系统支持至少10万用户的并发访问

### Dependencies

1. Epic 3 (健康数据记录) 完成 - 2026-02-26
2. 健康评估算法文档 - 2026-02-25

### Risks to Plan

- **Risk**: 健康评估算法需要外部专家评审
  - **Impact**: 可能延迟2-3天
  - **Contingency**: 准备备用的简化评估方案

---

## Follow-on Workflows (Manual)

- Run `*atdd` to generate failing P0 tests (separate workflow; not auto-run).
- Run `*automate` for broader coverage once implementation exists.

---

## Approval

**Test Design Approved By:**

- [ ] Product Manager: Date:
- [ ] Tech Lead: Date:
- [ ] QA Lead: Date:

**Comments:**

---

## Interworking & Regression

| Service/Component | Impact | Regression Scope |
| ----------------- | ------ | ---------------- |
| 用户系统 | 身份验证影响评估访问 | Epic 1 认证测试 |
| 健康数据系统 | 数据读取性能影响评估速度 | Epic 3 综合测试 |
| 历史评估数据 | 新旧评估结果对比 | Epic 6 趋势分析 |

---

## Appendix

### Knowledge Base References

- `risk-governance.md` - Risk classification framework
- `probability-impact.md` - Risk scoring methodology
- `test-levels-framework.md` - Test level selection
- `test-priorities-matrix.md` - P0-P3 prioritization

### Related Documents

- PRD: `/Users/felix/bmad/docs/PRD.md`
- Epic: `/Users/felix/bmad/_bmad_out/planning-artifacts/epics.md`
- Sprint Status: `/Users/felix/bmad/_bmad_out/implementation-artifacts/sprint-status.yaml`

---

**Generated by**: BMad TEA Agent - Test Architect Module
**Workflow**: `_bmad/tea/testarch/test-design`
**Version**: 5.0 (BMad v6)
