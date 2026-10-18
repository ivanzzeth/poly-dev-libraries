# Outbox

Go 实现已保存到 `go/infrastructure/containers/outbox`，包含 memory、PostgreSQL、Redis 三种后端。生产规模压测和故障切换演练尚未完成；最新查询优化仍待回归。

## 共享契约

- 核心接口与存储后端解耦：Writer、Consumer、Inspector、Admin，以及显式 Factory／Registry；不隐式建表、启动 worker 或管理宿主客户端生命周期。
- 事件使用稳定 ID；相同内容重复追加是无操作，不同内容返回冲突。消息载荷不可变。
- Claim 使用有界批次、租约与每次领取独立的令牌；Ack、Nack、Extend 校验领取权，过期领取不能继续修改状态。
- 投递允许重复；业务通过消息 ID 实现消费幂等。不保证 FIFO 或外部副作用恰好一次。
- 重试达到上限进入死信，可显式 Redrive；重放重置本轮尝试次数，保留累计次数和事件身份。
- Worker 提供并发限制、续租、超时和退避；存储错误终止 Run，由宿主监督与重启。回调必须响应 context 取消。

## 后端能力

memory 仅保留进程内状态。PostgreSQL 通过适配器的 `BindTx(ctx, name, *sql.Tx)` 返回 Writer，实现同一数据库内业务写入与事件追加的事务原子性。Redis 不提供业务事务绑定，也不保证跨存储原子性。

持久化能力不等于零数据丢失。PostgreSQL 的复制策略、Redis 的 AOF 与异步复制边界由部署决定；Redis WAIT 检查点不能变成所有后续写入的持久性保证。

## 规范与验证进度

- [接口与完整契约](../go/infrastructure/containers/outbox/DESIGN.md)
- [使用和真实后端测试](../go/infrastructure/containers/outbox/README.md)
- [暂停时的验证证据与换机续跑步骤](../go/infrastructure/containers/outbox/qualification/README.md)

之前的 Go 1.27.2 全库 build、vet、真实后端 race 检查已通过；此后新增的 PostgreSQL Claim 查询优化与演练草稿尚未完成验证，不能据此宣称生产验收完成。
