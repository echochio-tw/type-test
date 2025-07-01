# 中间者服务器 API 对接文档

本文档描述了客户游戏与直播平台之间“中间者”服务器的API接口。中间者服务器旨在协调客户游戏和直播平台之间的数据流，充当两者的桥梁。

**中间者服务器基地址：** `http://your_middleman_server_ip:5000` (请替换为你的实际服务器IP和端口)

---

## 1. 客户游戏 -> 中间者服务器

### 1.1 告知游戏开始并提供房间ID

此API用于客户游戏启动游戏会话，并通知中间者服务器当前游戏的直播间ID。中间者服务器在接收到此信息后，将与直播平台进行后续的交互（例如，启动数据推送任务，并可能模拟向直播间发送礼物）。

* **Endpoint:** `/game/start`
* **Method:** `POST`
* **Content-Type:** `application/json`
* **描述:** 客户游戏告知中间者游戏开始，并传递相关的直播间信息。
* **请求体 (Request Body):**

    ```json
    {
      "room_id": "string",  // 必填，当前游戏会话关联的直播间ID
      "user_id": "string"   // 可选，标识客户游戏用户的ID
    }
    ```

* **成功响应 (Success Response) - HTTP 200 OK:**

    ```json
    {
      "status": "success",
      "message": "游戏已开始，并已通知平台处理房间 {room_id}。"
    }
    ```

* **错误响应 (Error Response) - HTTP 400 Bad Request (例如，缺少 room_id):**

    ```json
    {
      "status": "error",
      "message": "缺少 room_id"
    }
    ```

* **错误响应 (Error Response) - HTTP 500 Internal Server Error (例如，中间者处理失败):**

    ```json
    {
      "status": "error",
      "message": "游戏启动流程中存在问题，请查看日志。"
    }
    ```

* **cURL 示例:**

    ```bash
    curl -X POST \
         -H "Content-Type: application/json" \
         -d '{
               "room_id": "YOUR_LIVE_ROOM_ID",
               "user_id": "YOUR_GAME_USER_ID"
             }' \
         http://your_middleman_server_ip:5000/game/start
    ```
    请将 `YOUR_LIVE_ROOM_ID` 和 `YOUR_GAME_USER_ID` 替换为实际值，并将 `your_middleman_server_ip` 替换为中间者服务器的实际IP地址。

---

## 2. 直播平台 -> 中间者服务器

### 2.1 接收平台推送数据回调

此API是中间者服务器提供给直播平台的Webhook回调地址。当直播平台有新的互动数据（如礼物、评论、点赞）时，它会向此URL发送POST请求，将数据推送给中间者服务器。

* **Endpoint:** `/platform/data_webhook`
* **Method:** `POST`
* **Content-Type:** `application/json`
* **描述:** 接收来自直播平台的实时互动数据推送。中间者服务器将在此处接收礼物、评论、点赞等信息，并可进一步处理或转发给客户游戏。
* **请求体 (Request Body):**
    请求体内容将根据直播平台推送的消息类型而异。以下是根据文档示例可能接收到的结构：

    **礼物推送示例:**
    ```json
    {
      "msg_id": "string",         // 消息唯一ID
      "gift_key": "string",       // 礼物唯一标识
      "room_id": 10008,           // 直播间ID (int64)
      "user_open_id": "string",   // 用户开放ID
      "user_name": "string",      // 用户名
      "user_avatar_url": "string",// 用户头像URL
      "gift_value": 10000,        // 礼物总价值，单位分 (int64)
      "gift_num": 100             // 礼物数量 (int)
    }
    ```

    **评论推送示例:**
    ```json
    {
      "msg_id": "string",         // 消息唯一ID
      "room_id": 10008,           // 直播间ID (int64)
      "user_open_id": "string",   // 用户开放ID
      "user_name": "string",      // 用户名
      "user_avatar_url": "string",// 用户头像URL
      "comment": "string"         // 评论内容
    }
    ```

    **点赞推送示例:**
    ```json
    {
      "msg_id": "string",         // 消息唯一ID
      "room_id": 10008,           // 直播间ID (int64)
      "user_open_id": "string",   // 用户开放ID
      "user_name": "string",      // 用户名
      "user_avatar_url": "string",// 用户头像URL
      "like_number": 10           // 点赞数量 (int)
    }
    ```

    *注意：* 直播平台可能还会发送其他消息类型，具体结构请参考直播平台提供的API文档。

* **签名校验:**
    为了确保数据完整性和安全性，强烈建议在此端点实现对直播平台推送数据的签名校验。具体校验逻辑请参考直播平台提供的相关文档（通常涉及对请求头、请求体和共享密钥的MD5或HMAC-SHA256哈希计算）。

* **成功响应 (Success Response) - HTTP 200 OK:**
    中间者服务器接收到数据并成功处理后，应返回一个简单的成功响应，告知直播平台数据已接收。

    ```json
    {
      "status": "received",
      "message": "数据已接收并处理"
    }
    ```

* **cURL 示例 (模拟直播平台推送礼物):**

    ```bash
    curl -X POST \
         -H "Content-Type: application/json" \
         -d '{
               "msg_id": "123456781",
               "gift_key": "pGLo7HKNk1i4djkicmJXf6iWEyd+pfPBjbsHmd3WcX0Ierm2UdnRR7UINVI=",
               "room_id": 10008,
               "user_open_id": "usr23353433224422433",
               "user_name": "test",
               "user_avatar_url": "[https://picsum.photos/800/600](https://picsum.photos/800/600)",
               "gift_value": 10000,
               "gift_num": 100
             }' \
         http://your_middleman_server_ip:5000/platform/data_webhook
    ```
    请将 `your_middleman_server_ip` 替换为中间者服务器的实际IP地址。示例值直接来源于您提供的文件。
