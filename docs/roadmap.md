# 组件状态与演进

## 当前交付

- Go：containers；Ethereum 的 ethclient、ethtypes、ethsig；Polymarket、Predict、Probable、Opinion 的 SDK／工具库。
- Python：ethclient.py。
- 聚合目录、固定提交、MIT 聚合许可、清单生成与 CI 校验。

除 containers 的 Outbox 实现、Go 1.27.2 升级与相关修复外，其他组件保持原有快照；不声明统一生产验收。
部分组件快照未包含根许可证文件，见生成目录。少数 SDK 使用本地 `replace`；其中 `opinion-go-contracts` 的 `../ethclient` 不符合当前领域分组，应在组件仓库修复可发布依赖后更新 gitlink。聚合层不偷偷覆盖它的模块解析。

## 第一批公共能力

1. **containers/outbox**：已在现有 UDC 仓库实现独立 package，支持 memory／PostgreSQL／Redis、有界 worker、领取令牌、重试／死信；PostgreSQL 支持同事务追加。下一步完成压测、故障演练和最后回归。
2. **数据库通用机制**：复用现有项目经过验证的连接、事务、重试与迁移装配；结合 containers 的持久化职责确定 package 归属，避免直接新增一个泛化 framework 或为每个函数建仓库。
3. **首个新项目接入**：以真实业务事务、重启恢复和幂等消费验证公共 API，形成最小可发布组件版本。
4. **旧项目渐进迁移**：优先替换重复的可靠投递机制，单独发布；保持原有消费者语义和必要回退能力。
5. **其他语言**：有实际消费者后按相同模式契约实现，允许 API 不同；生产能力分别验收。

## 状态约定

“已收录”指固定了公开源码；“计划”指尚未实现；“已验收”须关联具体组件提交、环境和测试结果。
Outbox 已有三后端实现、共享契约测试与 worker。生产规模压测和故障切换演练因换机暂停；最新查询优化待回归。详见 [当前契约与验证进度](../patterns/outbox.md) 和组件内的 qualification 交接记录。
