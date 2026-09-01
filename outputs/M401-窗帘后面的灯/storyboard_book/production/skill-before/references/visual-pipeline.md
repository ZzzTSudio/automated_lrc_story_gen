# AI视觉连续性与首帧生成

仅在用户需要角色图、场景图、逐镜首帧或图生视频提示时读取本文件。

## 1. 建立连续性圣经

在首次生成前锁定：

- 身份：年龄、脸型、眼型、眉形、鼻唇、肤色、皮肤质感。
- 发型：长度、分缝、刘海、盘发方式、胡须状态。
- 体型：身高、肩宽、比例、姿态。
- 服装：颜色、材质、领口、袖型、鞋、配饰；明确哪些镜头允许变化。
- 道具：形状、材质、磨损、颜色和持有者。
- 场景：平面结构、门窗、家具、镜面、屏幕、主光方向。
- 影像：画幅、焦段范围、现实或闪回的色彩与颗粒。

连续性描述要具体但不要堆砌无关审美词。

## 2. 角色设定图

默认使用16:9横版单人设定图：

- 左侧约40%：腰部以上半身细节，清楚展示脸、头发、妆容和服装材质。
- 右侧约60%：同一人物全身正面、90度侧面、背面，完整显示头到脚。
- 中性浅灰棚拍背景；柔和中性光；所有视图身份、比例、服装和配饰完全一致。
- 无文字、标签、拼贴边框、水印和品牌。

先生成核心主角，再根据剧情需要生成配角参考。角色图完成后必须视觉检查，确认不同视图没有换脸、换衣或身体比例漂移。

## 3. 场景锚点

为反复出现的空间先生成一个宽幅建立镜头，固定建筑结构、家具、门、屏幕、花艺和光源。角色可出现在锚点中，但后续引用时明确“仅引用空间，忽略锚点内人物”。

优先锚定主要现实场景、结尾会回到的场景，以及有镜子、玻璃、屏幕、门或复杂空间关系的场景。一次性闪回可只用文字设定。

## 4. 首帧提示结构

每个首帧提示按以下顺序组织：

```text
Use case: identity-preserve
Asset type: first frame <SHOT_ID> for a live-action AI video storyboard, true 16:9 landscape
Input images: <逐张说明角色或场景引用作用>
Primary request: <只描述第一帧可见画面>
Scene continuity: <空间与时间连续性>
Style/medium: high-definition photorealistic live-action drama still, professional cinema camera
Composition/framing: <景别、焦段、机位、构图>
Lighting/mood: <有动机的光线与情绪>
Motion intent: <后续数秒唯一主要运动>
Continuity constraints: preserve exact identity, hairstyle, proportions, outfit and referenced location
Output constraints: one single 16:9 frame; no collage, captions, readable generated text, logo or watermark
```

对输入图逐张标注角色。配角合并参考图必须明确使用左侧或右侧人物。引用顺序在同一批次保持稳定。

## 5. 图生视频动作提示

动作提示以首帧为前提，不重复完整场景描述。推荐结构：

```text
<一个主要人物动作或摄影机动作>;
preserve character identity and outfit;
natural blinking and breathing;
realistic cloth and hair physics;
stable background geometry;
no face drift, no extra people, no camera teleportation.
```

一个镜头只能有一个主要运动。需要第二个叙事动作时拆镜。

## 6. 精确文字与界面

LED屏、手机界面、邮件标题、直播人数和片尾字幕采用后期合成。首帧可以要求抽象界面、黑屏或无文字占位，但不要依赖图片模型准确写中文。

分镜书中标注后期文字原文、出现位置和持续时间，以及需要跟踪、反射或屏幕透视时的合成说明。

## 7. 批量生成策略

1. 角色设定图。
2. 场景锚点。
3. 三张不同复杂度的测试首帧：特写、双人、多人／反光。
4. 测试通过后按场景批量生成。
5. 每张成功后立即复制到稳定镜号文件名。
6. 记录失败项并单独重试，不重做成功项。
7. 生成结束后验证文件数量、尺寸和缺号，再做视觉总览抽查。

批量顺序可以按技术依赖而非叙事顺序执行，但最终文件必须按镜号排序。

## 8. 视觉验收

抽查必须覆盖开场人物和场景建立、核心道具特写、第一次信息反转、最复杂的多人动作镜头、闪回或特殊光线镜头，以及结尾回收镜头。

发现单张错误时做定点重生或编辑，不要无理由重生整批。允许后期解决的文字内容不应触发整图返工；身份、手部、关键道具和空间错误必须修复。
