# 给遊戲方 API 文件

這份文件旨在說明遊戲方服務告知平台服務遊戲開始。

---

## 基礎 URL

API 運行在 `https://mg3admin.nbfmg.com/`。

---

## 端點

### 1. 遊戲初始化

透過向平台服務請求 `game_id` 來初始化一個新的遊戲會話。

* **URL:** `/api/game/initiate`
* **方法:** `POST`
* **描述:** 此端點模擬了來自 PC 遊戲客戶端的遊戲啟動請求。它內部會呼叫平台服務以獲取該會話的唯一 `game_id`。
* **請求主體:** (此模擬端點不直接接收來自客戶端的請求主體，範例中參數為硬編碼以供示範。)

    內部向平台服務 (`https://mg3admin.nbfmg.com/game/init`) 發送的 JSON 負載如下：

    ```json
    {
        "game_mode": "single",
        "game_type": "sgs",
        "room_id": "10001",
        "anchor_id": "anchor_abc",
        "start_time": 1719900000
    }
    ```

* **成功響應:**
    * **狀態碼:** `200 OK`
    * **內容:**

        ```json
        {
            "status": "success",
            "message": "遊戲已啟動",
            "game_id": "你的 game_id"
        }
        ```

* **錯誤響應:**
    * **狀態碼:** `500 Internal Server Error`
    * **內容 (範例 1：無法從平台獲取遊戲 ID):**

        ```json
        {
            "status": "error",
            "message": "無法從平台方獲取遊戲ID"
        }
        ```

    * **內容 (範例 2：與平台通訊失敗):**

        ```json
        {
            "status": "error",
            "message": "與平台方通訊失敗: <錯誤詳情>"
        }
        ```

---

## 2. 直播平台 -> 平台服務遊
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
      [cite_start]"msg_id": "string",         // 消息唯一ID [cite: 151, 156]
      [cite_start]"gift_key": "string",       // 礼物唯一标识 [cite: 152, 157, 255, 257]
      [cite_start]"room_id": 10008,           // 直播间ID (int64) [cite: 153, 158, 236, 256, 258, 303]
      [cite_start]"user_open_id": "string",   // 用户开放ID [cite: 154, 159, 237, 259]
      [cite_start]"user_name": "string",      // 用户名 [cite: 155, 160, 240, 260]
      [cite_start]"user_avatar_url": "string",// 用户头像URL [cite: 161, 241, 261]
      [cite_start]"gift_value": 10000,        // 礼物总价值，单位分 (int64) [cite: 162, 165]
      [cite_start]"gift_num": 100             // 礼物数量 (int) [cite: 163, 166, 242, 262]
    }
    ```

    **评论推送示例:**
    ```json
    {
      [cite_start]"msg_id": "string",         // 消息唯一ID [cite: 192, 193]
      [cite_start]"room_id": 10008,           // 直播间ID (int64) [cite: 194, 197]
      [cite_start]"user_open_id": "string",   // 用户开放ID [cite: 195, 198]
      [cite_start]"user_name": "string",      // 用户名 [cite: 196, 199]
      [cite_start]"user_avatar_url": "string",// 用户头像URL [cite: 200]
      [cite_start]"comment": "string"         // 评论内容 [cite: 201, 202]
    }
    ```

    **点赞推送示例:**
    ```json
    {
      [cite_start]"msg_id": "string",         // 消息唯一ID [cite: 179, 183]
      [cite_start]"room_id": 10008,           // 直播间ID (int64) [cite: 180, 184]
      [cite_start]"user_open_id": "string",   // 用户开放ID [cite: 181, 185]
      [cite_start]"user_name": "string",      // 用户名 [cite: 182, 186]
      [cite_start]"user_avatar_url": "string",// 用户头像URL [cite: 187]
      [cite_start]"like_number": 10           // 点赞数量 (int) [cite: 188, 189]
    }
    ```

    *注意：* 直播平台可能还会发送其他消息类型，具体结构请参考直播平台提供的API文档。

* **签名校验:**
    [cite_start]为了确保数据完整性和安全性，强烈建议在此端点实现对直播平台推送数据的签名校验。具体校验逻辑请参考直播平台提供的相关文档（通常涉及对请求头、请求体和共享密钥的MD5或HMAC-SHA256哈希计算）。

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
             }' 
         https//mg3admin.nbfmg.com/platform/data_webhook
    ```
   
