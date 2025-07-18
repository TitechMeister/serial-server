# API Information <!-- omit in toc -->

- [base URL: `localhost:{port}`](#base-url-localhostport)
- [`/serial/`](#serial)
  - [`GET /serial/state`](#get-serialstate)
  - [`GET /serial/available_ports`](#get-serialavailable_ports)
  - [`POST /serial/connect`](#post-serialconnect)
  - [`POST /serial/disconnect`](#post-serialdisconnect)
  - [`POST /serial/write`](#post-serialwrite)
- [`/data/`](#data)
  - [`GET /data`](#get-data)
  - [`GET /data/<parsername>`](#get-dataparsername)
- [`/parsers/`](#parsers)
  - [`GET /parsers`](#get-parsers)
  - [`GET /parser/<parsername>`](#get-parserparsername)
- [その他](#その他)
  - [`GET /test`](#get-test)
  - [`GET /help`](#get-help)
  - [`GET /`](#get-)

## base URL: `localhost:{port}`

port_numberはデフォルトが7878で、起動時にオプション-pまたは--portを用いることで変更できます。

## `/serial/`

ポート設定やシリアルへの書き込みなど、シリアル通信を直接制御するためのエンドポイント群です。

### `GET /serial/state`

#### 概要

現在のシリアルポートの状態を取得します。

#### レスポンス

**200 OK**

```json
{"state": state}
```

`state`には`"CONNECTED"`, `"DISCONNECTED"`, `"READING"`, `"ERROR"`のどれかが入ります。

#### 具体例

```json
{"state": "CONNECTED"}
```

### `GET /serial/available_ports`

#### 概要

現在接続可能なシリアルポートの一覧を取得します。

#### レスポンス

**200 OK**

```json
{"available_ports": [port]}
```

`[port]`には次の形式のデータが配列となって入ります。

```json
{
    "device": "{device name}",
    "description": "{description}",
    "hwid": "{hwid}"
}
```

#### 具体例

```json
{
    "available_ports": [
        {"description":"n/a","device":"/dev/cu.debug-console","hwid":"n/a"},
        {"description":"n/a","device":"/dev/cu.VictorHA-A20T","hwid":"n/a"},
        {"description":"n/a","device":"/dev/cu.Bluetooth-Incoming-Port","hwid":"n/a"},
        {"description":"IOUSBHostDevice","device":"/dev/cu.usbmodem1101","hwid":"USB VID:PID=2341:0043 SER=8513831393335161E082 LOCATION=0-1.1"}
    ]
}
```

### `POST /serial/connect`

#### 概要

指定されたシリアルポートに接続します。

#### リクエストボディ

**Content-Type**: `application/json`

```json
{
    "portname": port name,
    "baudrate": baudrate
}
```

- `portname` (必須): 接続するポート名、available_portsでの"device"の値を用いる
- `baudrate` (オプション): ボーレート（デフォルト: 115200）

#### レスポンス

**200 OK**

```json
{"status": "connected"}
```

**400 Bad Request**

```json
{"error": "Port name is required"}
```

**500 Internal Server Error**

```json
{"error": "Failed to connect"}
```

#### 具体例

**リクエスト:**

```json
{
    "portname": "/dev/cu.usbmodem1101",
    "baudrate": 115200
}
```

**レスポンス:**

```json
{"status": "connected"}
```

### `POST /serial/disconnect`

#### 概要

現在接続されているシリアルポートから切断します。

#### レスポンス

**200 OK**

```json
{"status": "disconnected"}
```

**204 No Content**

```json
{"status": "port is not open"}
```

#### 具体例

```json
{"status": "disconnected"}
```

### `POST /serial/write`

#### 概要

現在開いているシリアルポートにデータを書き込みます。

#### リクエストボディ

**Content-Type**: `application/json`

```json
{
    "payload": [byte],
}
```

`[byte]`はすべて0~255の範囲内の整数の配列である必要があります。

#### レスポンス

**200 OK**

```json
{"status": "data sent"}
```

**400 Bad Request**

```json
{"error": "Payload is required"}
```

**500 Internal Server Error**

エンコードに失敗した場合(payloadのvalueが正しくない時など)

```json
{"error": "Encoding error: {error}"}
```

エンコードには成功したが、送信に失敗した場合

```json
{"error": "port is not open or failed to write"}
```

#### 具体例

**リクエスト:**

```json
{
    "portname": "/dev/cu.usbmodem1101",
    "baudrate": 115200
}
```

**レスポンス:**

```json
{"status": "connected"}
```

## `/data/`

パーサーによって解析されたシリアルデータを取得するためのエンドポイント群です。
すべてのデータは最新のデータを表示します。過去のデータは新しいデータによって上書きされていくため、予想されるデータの更新頻度に合わせてアクセスしてください。

### `GET /data`

#### 概要

全てのパーサーから取得された解析済みデータを一度に取得します。

#### レスポンス

**200 OK**

```json
{
    "parsername1": {parsed_data},
    "parsername2": {parsed_data},
    ...
}
```

`{parsed_data}`は`parser/<parsername>`で取得できる`"keys"`の値をkeyに持ちます。

#### 具体例

```json
{
    "gps": {
        "latitude": 35.6762,
        "longitude": 139.6503,
        "altitude": 40.0
    },
    "tachometer": {
        "rpm": 1200
    }
}
```

### `GET /data/<parsername>`

#### 概要

指定されたパーサーの解析済みデータを取得します。

#### パラメータ

- `parsername`: パーサー名

#### レスポンス

**200 OK**

```json
{parsed_data}
```

**404 Not Found**

```json
{
    "error": "No data found for this parser",
    "available": [available_parser_names]
}
```

#### 具体例

**リクエスト:** `GET /data/gps`

**レスポンス:**

```json
{
    "latitude": 35.6762,
    "longitude": 139.6503,
    "altitude": 40.0
}
```

## `/parsers/`

利用可能なパーサーに関する情報を取得するためのエンドポイント群です。

### `GET /parsers`

#### 概要

利用可能なパーサーの一覧を取得します。

#### レスポンス

**200 OK**

```json
{"parsers": [parser_names]}
```

#### 具体例

```json
{
    "parsers": [
        "gps",
        "tachometer",
        "thrustmeter",
        "ultrasonic"
    ]
}
```

### `GET /parser/<parsername>`

#### 概要

指定されたパーサーの詳細情報を取得します。

#### パラメータ

- `parsername`: パーサー名

#### レスポンス

**200 OK**

```json
{
    "name": "{parser_name}",
    "keys": [data_key_names],
}
```

**404 Not Found**

```json
{"error": "Parser not found"}
```

#### 具体例

**リクエスト:** `GET /parser/gps`

**レスポンス:**

```json
{
    "name": "gps",
    "keys": ["latitude", "longitude", "altitude"],
}
```

## その他

### `GET /test`

#### 概要

サーバーの動作確認用のテストエンドポイントです。

#### レスポンス

**200 OK**

```json
{"message": "This is a test endpoint"}
```

### `GET /help`

#### 概要

APIの使用方法を説明するHTMLページを返します。

#### レスポンス

**200 OK**

**Content-Type**: `text/html`

APIエンドポイントの一覧と説明が記載されたHTMLページが返されます。

### `GET /`

#### 概要

ルートアクセス時に`/help`と同じHTMLページを返します。

#### レスポンス

**200 OK**

**Content-Type**: `text/html`

`/help`エンドポイントと同じHTMLページが返されます。

