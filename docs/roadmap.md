# 组件状态与演进

## 当前交付

- Go：containers；Ethereum 的 ethclient、ethtypes、ethsig；Polymarket、Predict、Probable、Opinion 的 SDK／工具库。
- Python：ethclient.py。
- 聚合目录、固定提交、MIT 聚合许可、清单生成与 CI 校验。

组件原有实现均保持不变，本次不升级其依赖、不执行线上 API 或交易操作、不声明统一生产验收。
部分组件快照未包含根许可证文件，见生成目录。少数 SDK 使用本地 `replace`；其中 `opinion-go-contracts` 的 `../ethclient` 不符合当前领域分组，应在组件仓库修复可发布依赖后更新 gitlink。聚合层不偷偷覆盖它的模块解析。

## 第一批公共能力

1. **containers/outbox**：在现有 UDC 仓库增加独立 package，先做同事务追加与 PostgreSQL 后端、有界 worker、领取令牌、重试／死信与重复投递契约。实现前核验现有 message、queue、metrics 的可复用部分。
2. **数据库通用机制**：复用现有项目经过验证的连接、事务、重试与迁移装配；结合 containers 的持久化职责确定 package 归属，避免直接新增一个泛化 framework 或为每个函数建仓库。
3. **首个新项目接入**：以真实业务事务、重启恢复和幂等消费验证公共 API，形成最小可发布组件版本。
4. **旧项目渐进迁移**：优先替换重复的可靠投递机制，单独发布；保持原有消费者语义和必要回退能力。
5. **其他语言**：有实际消费者后按相同模式契约实现，允许 API 不同；生产能力分别验收。

## 状态约定

“已收录”指固定了公开源码；“计划”指尚未实现；“已验收”须关联具体组件提交、环境和测试结果。
Outbox 目前仅有 [模式草案](../patterns/outbox.md)，不代表 UDC 已提供该能力。后续增加可执行测试向量时同时维护模式版本及语言／后端验收状态。
