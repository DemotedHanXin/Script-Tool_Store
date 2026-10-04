# JetBrains AI 模型列表诊断

诊断日期：2026-10-04。状态：已定位当前 CLion 的直接失败原因，尚未完成更换代理后的恢复验证。

## 结论

AI Assistant 262.10968.169 在第三方提供商模型列表加载外层硬编码了 2500 毫秒超时。当前 HTTP 代理访问 OpenAI 接口的延迟超过这一预算，触发 TimeoutCancellationException。插件将此异常作为控制流取消向上传递，没有发布模型列表；界面随后等待列表 45 秒并显示无模型。

CLion 实测异常链已确认。PyCharm、IDEA 使用相同插件版本、代理且有相同列表等待超时，因此该机制也很可能解释它们的症状，但未对二者分别抓取 JFR 复现。

## 证据

- CLion 23:29:40.014：LlmProfileService 记录 `updating available llm profiles`。
- 23:29:42.519：JFR 记录 TimeoutCancellationException，随后 Ktor HTTP 请求取消。
- 23:29:42.520：AiaThirdPartyLlmProviderClient$getAvailableProfiles$3 与 LlmProfileService 在 rethrowControlFlowException 重新抛出取消。
- 本机插件字节码：AiaThirdPartyLlmProviderClient$loadAvailableProfiles$2 使用常数 2500 ms 调用 withTimeout；内部调用 provider.getAvailableLLMs()。
- 三次不带 API 密钥的代理链路测试：访问 https://api.openai.com/v1/models，总用时 3.496654、3.639405、3.760705 秒；TLS 建立用时 3.088943、3.175456、2.929498 秒。401 是不带密钥时的预期状态，仅用于计时，不代表用户配置的密钥无效。
- IDE 自身测试连接返回 connected。连接测试与正式列表加载的外层超时处理不同，故两种现象可以同时存在。

## 处理建议

1. 优先将 v2rayN 切到访问 OpenAI 更快、更稳定的线路，使模型列表完整请求低于 2.5 秒并留有余量。普通节点 ping 延迟不能代替 API 请求总时间。
2. 切到其他窗口后再返回已打开项目的 CLion，插件注册的 applicationActivated 监听器会重新加载模型；检查模型下拉列表。
3. 恢复后再验证 PyCharm 和 IDEA。若所有可用线路仍超过预算，应考虑向 JetBrains 报告该超时/取消处理问题，或验证后续官方插件是否修复；目前没有确认已修复的版本。

当前实现没有可调 Registry/设置项。OpenAI 兼容提供商也需要请求模型清单，手工选择默认模型不能绕开该加载步骤。重新填写密钥、切换 Toolbox 登录、扩大通用 IDE HTTP 超时不改变这个 2500 ms 限制。

## 本次诊断修改

- API Key 未读取、未改写；聊天历史未修改。
- CLion 供应商曾临时切换用于诊断，已恢复 OpenAI。
- 外部原始 VM options 与原有启动环境未修改；工作目录中的一次性 PyCharm 诊断文件不影响正常启动。
- 短时 JFR 自动结束。窄范围 DEBUG 日志在诊断完成后关闭。

本文件不包含密钥、令牌或聊天内容。
