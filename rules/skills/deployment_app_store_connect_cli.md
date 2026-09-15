# 使用 Apple 官方命令行工具发布 App Store Connect

## 元数据

- **类型**：Deployment
- **适用场景**：通过非 beta 版 Xcode 在命令行完成 iOS App 的 archive、App Store 签名导出与 App Store Connect 上传
- **输出**：可审计的 `.xcarchive`、App Store `.ipa`、上传结果与版本信息
- **创建日期**：2026-07-31
- **更新**：2026-09-11

## 目标与边界

只使用 Xcode 自带的 Apple 官方工具，把一个可发布的 Xcode scheme 转换成 App Store Connect 已接收的 build。Agent 可以根据工程形态调整参数，但必须保留源码版本、构建配置、签名身份、产物 metadata 和远端接收状态之间的证据链。

本 skill 不创建自定义 CLI，不管理商店截图、描述、定价或审核提交，也不把“上传成功”误报为“已经发布到 App Store”。

- 本地检查、build、test、archive 和 `destination=export` 的 IPA 导出可以自主执行。
- `destination=upload` 或 `altool --upload-*` 会向 App Store Connect 写入 build，执行前必须获得用户对本次上传的明确授权。
- 上传后不要自动提交 TestFlight 外部测试、App Review 或修改商店 metadata，除非用户另行授权。
- 不在命令、日志或仓库中明文写 Apple ID 密码、App 专用密码、API private key、Issuer ID、Team ID 或 provisioning profile UUID。

## 验收标准

- `DEVELOPER_DIR` 明确指向预期的稳定版 Xcode，`xcodebuild -version` 与发布记录一致。
- 目标 scheme 是 shared scheme，Release 配置能针对 `generic/platform=iOS` 构建，仓库要求的 build 和 test 已通过。
- `.xcarchive` 生成成功，bundle identifier、marketing version、build number、签名 team 和最低系统版本符合预期。
- 使用 `method=app-store-connect` 成功导出；摘要显示 Apple Distribution 或 Cloud Managed Apple Distribution、有效的 App Store provisioning profile，且 `get-task-allow=false`。
- 从最终 IPA 再次读取 `CFBundleShortVersionString`、`CFBundleVersion` 和 `MinimumOSVersion`，不能只相信工程配置。
- 上传命令返回 `Upload succeeded` 或同等成功状态，App Store Connect 已接受 package 并开始 processing。
- 如果任务要求等待处理完成，还必须查询 processing 状态；`Uploaded package is processing` 不等于处理完成。

## Apple 官方工具

- `xcode-select`：查看或切换当前 Xcode developer directory。
- `xcodebuild`：列举 scheme、build、test、archive、导出和直接上传。
- `xcrun altool`：使用 App Store Connect API key 或 App 专用密码执行显式 validate/upload/status 查询。
- `codesign`、`plutil`、`unzip`：核验签名与最终 IPA metadata。

## 发布方法

### 固定稳定版 Xcode

```bash
export DEVELOPER_DIR="/Applications/Xcode.app/Contents/Developer"
xcode-select -p
xcodebuild -version
```

如果稳定版 Xcode 安装在其他路径，使用实际路径。机器上并存 `Xcode-beta.app` 时不要依赖模糊的全局选择，也不要为了让命令通过而删除 beta Xcode。

### 识别工程与签名条件

```bash
xcodebuild -project <App.xcodeproj> -list
xcodebuild \
  -project <App.xcodeproj> \
  -scheme <SharedScheme> \
  -configuration Release \
  -destination 'generic/platform=iOS' \
  -showBuildSettings
security find-identity -v -p codesigning
```

至少核对 `PRODUCT_BUNDLE_IDENTIFIER`、`MARKETING_VERSION`、`CURRENT_PROJECT_VERSION`、`IPHONEOS_DEPLOYMENT_TARGET`、`DEVELOPMENT_TEAM` 和 `CODE_SIGN_STYLE`。Automatic Signing 可以在 export 阶段使用 Cloud Managed Apple Distribution，因此本机没有可见的 Apple Distribution identity 不等于无法发布；最终以导出结果为准。

### Archive

```bash
xcodebuild archive \
  -project <App.xcodeproj> \
  -scheme <SharedScheme> \
  -configuration Release \
  -destination 'generic/platform=iOS' \
  -archivePath <output/App.xcarchive> \
  -allowProvisioningUpdates \
  CODE_SIGN_STYLE=Automatic \
  DEVELOPMENT_TEAM=<TEAM_ID>
```

每次重试使用新的输出路径，或者在确认旧产物不再需要后再清理。

### App Store 导出

使用临时 `ExportOptions.plist`；此文件不应进入公开仓库：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>destination</key><string>export</string>
  <key>method</key><string>app-store-connect</string>
  <key>signingStyle</key><string>automatic</string>
  <key>teamID</key><string>TEAM_ID</string>
  <key>uploadSymbols</key><true/>
</dict>
</plist>
```

```bash
xcodebuild -exportArchive \
  -archivePath <output/App.xcarchive> \
  -exportPath <output/export> \
  -exportOptionsPlist <output/ExportOptions.plist> \
  -allowProvisioningUpdates
```

Xcode 默认可能通过 `manageAppVersionAndBuildNumber` 把导出 IPA 的 build number 调整为 App Store Connect 可接受的下一值。必须以 `DistributionSummary.plist` 和最终 IPA 为准，并记录源码 build number 与上传 build number 是否不同。需要完全由源码控制版本时，应显式关闭该行为并提前更新工程 build number。

### 核验最终 IPA

```bash
unzip -p <App.ipa> Payload/<AppName>.app/Info.plist \
  | plutil -extract CFBundleShortVersionString raw -
unzip -p <App.ipa> Payload/<AppName>.app/Info.plist \
  | plutil -extract CFBundleVersion raw -
unzip -p <App.ipa> Payload/<AppName>.app/Info.plist \
  | plutil -extract MinimumOSVersion raw -
```

metadata 与预期不符时，修正工程后重新 build、test、archive、export；不要上传错误产物。

### 上传

获得明确授权后，把 export options 的 `destination` 改成 `upload`，然后调用：

```bash
xcodebuild -exportArchive \
  -archivePath <output/App.xcarchive> \
  -exportPath <output/upload> \
  -exportOptionsPlist <output/UploadOptions.plist> \
  -allowProvisioningUpdates
```

使用独立 App Store Connect API key 时，也可以调用官方 `altool`：

```bash
xcrun altool --validate-app -f <App.ipa> \
  --api-key <KEY_ID> --api-issuer <ISSUER_ID>
xcrun altool --upload-app -f <App.ipa> \
  --api-key <KEY_ID> --api-issuer <ISSUER_ID>
```

私钥应位于 Apple 官方支持的 private key 搜索目录或由受控环境提供；不要把 `.p8` 内容写进命令历史。

用 App 专用密码（而非 API key）调用 `altool` 时，若该 Apple ID 绑定了多个 provider，必须加 `--provider-public-id <PROVIDER_PUBLIC_ID>`；不带该参数首次运行会列出各 provider 的 Name 与 Public ID。只读查询（如 `--list-apps`）可用 1Password 里的 app-specific password（例如 `op read 'op://dev/dev-api-keys/icloud_app_specific_password'`），不要写明文。注意：app-specific password 查不到单个 build 的 processing 状态，那需要 ASC API key 或 App Store Connect web。

## 已知陷阱

### Xcode 工程默认了当前最新 OS

新建工程可能把 `IPHONEOS_DEPLOYMENT_TARGET` 设成当前 SDK 对应的最新系统，而产品实际支持更早版本。archive 仍会成功，但用户覆盖范围会被无意缩窄。发布前必须同时核对工程设置和 IPA 的 `MinimumOSVersion`。

### Archive 成功不代表可以上传

archive 常使用 Apple Development identity。App Store export 才会重签成 Apple Distribution 或 Cloud Managed Apple Distribution，并绑定 App Store provisioning profile。

### 本机看不到 Distribution certificate 仍可能导出成功

Automatic Signing 可以借助 Xcode 登录状态和云管理证书完成 distribution export。不要仅凭 `security find-identity` 没列出 Apple Distribution 就停止；应先执行不上传的 `destination=export` 验证。

### 源码 build number 不一定等于 IPA build number

Xcode managed versioning 可能在导出时查询 App Store Connect 并选择下一 build number。记录和重复上传都必须读取最终 IPA。

### Upload succeeded 不等于 processing succeeded

`Upload succeeded` 只说明 Apple 接受了 package。任务若以“上传”为终点，应准确报告“已上传并进入 processing”；若以“可选作 TestFlight build”为终点，则必须继续等待处理完成。

### Team Store Profile 不含云托管 Distribution 证书

`method=app-store-connect` + `signingStyle=automatic` 走云托管签名时，Apple 会在 distribution 证书到期前约 90 天自动轮换证书。若 portal 上的 "iOS Team Store Provisioning Profile" 仍引用旧证书，export 会在重签前的 qualification 阶段报 `Provisioning profile "iOS Team Store Provisioning Profile: <bundle-id>" doesn't include signing certificate "Apple Distribution: <team>"`，或 `failed qualification checks`。Xcode 不会自动刷新该 profile，除非命令带了 `-allowProvisioningUpdates`。修复：给 archive / export / upload 加 `-allowProvisioningUpdates`，让 Xcode 重建 profile。不要尝试在 Apple Developer portal 手动删除 Xcode 托管的 profile——它通常不在 portal 列表里，删不掉；若加 flag 仍失败，删除本机两处缓存 profile 后重跑：`~/Library/Developer/Xcode/UserData/Provisioning Profiles/`（Xcode 16+）与 `~/Library/MobileDevice/Provisioning Profiles/`（legacy），用 `security cms -D -i <file>` 按 Name 定位到对应 bundle id 的条目。

## 故障诊断

命令失败时，不要只读终端最后一行。`xcodebuild -exportArchive` 每次都会生成一个 `.xcdistributionlogs` 日志 bundle（终端会打印其路径），读其中的 `IDEDistribution.standard.log`，按 step 定位卡点：

- 停在 `IDEDistributionUploadAccountStep` 且出现 `Failed to find an account with App Store Connect access for team ...`：Xcode 里没有已登录且带 App Store Connect 权限的 Apple ID。云托管签名完全依赖这个登录态，到 Xcode → Settings → Accounts 登录或重新认证（2FA）。可用 `plutil -p ~/Library/Preferences/com.apple.dt.Xcode.plist | grep -A6 DVTDeveloperAccountManagerAppleIDLists` 检查登录态；该 plist 由稳定版与 beta **共享**，所以账号缺失通常不是"某个 Xcode 版本有、另一个没有"的版本差异问题。
- 卡在 profile qualification（`failed qualification checks` / `doesn't include signing certificate`）：profile 与当前解析到的 distribution 证书不匹配，见上方陷阱条目，加 `-allowProvisioningUpdates` 修复。
- `No signing certificate "iOS Distribution" found`：多为"无登录账号"的表象，先按登录态排查，而不是去 keychain 找本地 distribution 证书。

诊断只读日志与账号状态，不改动 portal 资源；真正的修复动作仍按上方方法与授权边界执行。

## 输出规格

最终报告至少包含 Xcode 路径与版本、源码 revision 或工作区状态、scheme 与 configuration、bundle identifier、marketing version、最终 build number、最低 iOS 版本、archive/IPA 路径、distribution certificate 与 profile 类型、各阶段状态、App Store Connect 当前 processing 状态，以及未执行的 TestFlight 分发或审核动作。
