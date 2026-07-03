# Mac Universal Clipboard 重置技能

## 目标

当用户说 Mac 和 iPhone/iPad 之间的 Universal Clipboard、Handoff 剪贴板或跨设备复制粘贴不同步时，使用本技能。典型形态是 iPhone 和 iPad 之间仍然正常，但只要经过 Mac 就失败。macOS beta 版本里，这通常是 Mac 端 Continuity daemon 持有了过期状态。

## 触发条件

用户提到这些现象时触发："Mac Universal Clipboard 不工作"、"clipboard 不 sync"、"手机和 Mac 剪贴板断了"、"iPhone copy Mac paste 不行"、"iPad 和 Mac 不能复制粘贴"、"Handoff clipboard broken"、"Universal Clipboard stopped syncing"，或同义表达。

## 快速修复

如果用户已经授权在本机排障，直接运行：

```bash
defaults delete ~/Library/Preferences/com.apple.coreservices.useractivityd.plist ClipboardSharingEnabled 2>/dev/null; \
defaults write ~/Library/Preferences/com.apple.coreservices.useractivityd.plist ClipboardSharingEnabled 1; \
killall useractivityd 2>/dev/null; \
killall sharingd 2>/dev/null; \
killall pboard 2>/dev/null; \
sleep 2; \
pgrep -fl 'useractivityd|sharingd|pboard'
```

预期结果：`useractivityd`、`sharingd`、`pboard` 会被 launchd 自动拉起，并重新出现在进程列表里。随后让用户测试 iPhone/iPad -> Mac 和 Mac -> iPhone/iPad 两个方向的复制粘贴。

## 原理

Mac 端 Universal Clipboard 主要依赖三层：

1. `pboard` 管本地 pasteboard 状态。
2. `useractivityd` 管 Handoff / Continuity activity 状态，包括 Universal Clipboard 偏好和共享剪贴板 blob。
3. `sharingd` 管附近设备发现和 sharing transport。

当 iPhone 和 iPad 之间仍然能同步，但 Mac 被隔离时，Apple ID 和 iOS 端 Handoff 大概率正常。重写 Mac 端 `ClipboardSharingEnabled` 并重启这三个 daemon，比重启电脑或退出 iCloud 成本低。

## 可选诊断

只有快速修复失败，或用户想确认根因时再做诊断。

```bash
sw_vers
defaults read ~/Library/Preferences/com.apple.coreservices.useractivityd.plist ClipboardSharingEnabled 2>/dev/null
pgrep -fl 'pboard|useractivityd|sharingd|bluetoothd'
ls -la ~/Library/Group\ Containers/group.com.apple.coreservices.useractivityd/shared-pasteboard/ 2>/dev/null
/usr/bin/log show --predicate 'process == "useractivityd"' --last 30m --style compact 2>/dev/null | tail -30
/usr/bin/log show --predicate 'process == "sharingd"' --last 30m --style compact 2>/dev/null | tail -30
```

在 zsh 里用 `/usr/bin/log`，不要直接用 `log`，因为某些环境里 `log` 可能解析成 shell builtin 或 function。

## 升级处理

如果快速修复无效：

1. 让用户在 Mac 的 System Settings -> General -> AirDrop & Handoff，以及 iOS/iPadOS 的 Settings -> General -> AirPlay & Handoff 里关开 Handoff。
2. 让 Mac 进入一次 Safe Mode，再正常重启。这个动作会清理一批系统缓存，历史上对 macOS 更新后 Continuity 状态异常有效。
3. 可以考虑删除 Keychain 里的 `handoff-own-encryption-key`，再重启 Handoff。这样会让 Mac 重新生成本机 Handoff 身份密钥。
4. 把退出 iCloud 再登录作为最后手段。这个动作会触发 iCloud Drive、Photos、Keychain 等重新同步，打扰较大。

如果机器运行的是 macOS beta，快速修复失败后优先按系统回归判断。症状符合 beta Continuity bug 时，不要反复叠加更重的本地改动。
