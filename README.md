# poly-dev-libraries

多语言研发基础库集合，按 **语言 → 领域 → 独立库** 组织。通用容器、协议客户端、平台 SDK 和领域工具库通过 Git 子模块统一管理，组件保留各自的仓库、包路径、版本和发布流程。

当前收录 **22 个 Go 库、1 个 Python 库**。收录表示目录与源码版本已固定，不表示所有组件已经通过统一生产验收。完整清单及许可证文件状态见 [CATALOG.md](CATALOG.md)。

```text
go/
├── infrastructure/containers/    # go-universal-data-containers
├── web3/ethereum/                # ethclient、ethtypes、ethsig
└── prediction-markets/           # polymarket、predict、probable、opinion
python/
└── web3/ethereum/ethclient.py/
patterns/                        # 跨语言共享行为规范
```

## 获取与使用

```sh
git clone --recurse-submodules https://github.com/ivanzzeth/poly-dev-libraries.git
cd poly-dev-libraries
make check
```

已有 checkout 初始化或切换聚合版本后执行：

```sh
git submodule update --init --recursive
```

只取一个库可执行 `git submodule update --init go/infrastructure/containers`。
应用按组件原有说明通过 Go modules 或对应语言的包管理方式依赖组件；本仓库不提供统一 Go module，也不自动覆盖应用的依赖版本。Python 组件的安装方式以其自身说明为准。

## 维护原则

- 新项目优先依赖已交付公共组件；缺失的通用能力直接在所属组件库完善，业务项目保留适配与领域逻辑。
- 老项目按模块渐进迁移，保留原有行为对照与回退路径，不因归档整理同时升级组件版本。
- 一个内聚的库可包含多个 package；Outbox 归入 containers，不因一个设计模式新增一个仓库。
- 跨语言复用行为规范与验收场景，各语言保留自然的 API；内存、Redis 与 PostgreSQL 的能力差异必须明确。
- 成熟第三方实现优先复用或薄适配；独立服务、业务应用与废弃参考项目不属于本目录。

## 文档与检查

- [架构与边界](docs/architecture.md)
- [新增、升级与迁移流程](docs/contributing.md)
- [组件状态与首批演进](docs/roadmap.md)
- [共享模式](patterns/README.md) · [Transactional Outbox 草案](patterns/outbox.md)

`make check` 校验清单、Git 子模块、固定提交、目录分类及生成目录的一致性；`make check-checkouts` 进一步检查本地子模块版本和 Go module 路径。它们不运行 SDK 网络调用或组件业务测试，不能代替组件自身 CI。

## 许可证

本聚合仓库自行编写的文档和工具使用 [MIT](LICENSE)。各子模块遵循各自许可证；聚合仓库的许可证不覆盖或替代组件许可证。清单中未发现许可证文件的组件标为待核对，不为它们补写或推断许可。
