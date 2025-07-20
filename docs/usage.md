# Serial-Server 使い方

## 必要ソフト

python3

## 初期設定

仮想環境の初期設定を行います。

```shell
$ source setup.sh
```

## 起動方法

まず、仮想環境を立ち上げます。

```shell
$ source .venv/bin/activate
```

その後、本アプリを起動します。

```shell
$ python3 serialserver.py
```

起動するポート番号を変えたい場合は、`-p`または`--port`オプションを用いてください。デフォルトは7878です。

例.20000ポートで立ち上げたい場合

```shell
$ python3 serialserver.py -p 20000
```

## parserの追加方法

このアプリでは、parserを追加することでバイト列を自動で辞書型に変換し、jsonとして出力することができます。

`background/parsers/`の中に`parser`という名前のインスタンスを定義したモジュールを置いておくと、自動で読み込みます。
ただし、`parser`は`background/abstractparser.py`モジュールの中にある、`AbstractParser`クラスを継承したクラスのインスタンスである必要があります。

注意：parserインスタンスが定義されていないファイルを置いてしまうと、実行時エラーになるので注意してください。parserインスタンスを定義しないモジュールは、`background/parsers`以外の場所においてください。

### 例.

C言語で以下の構造体に対応するデータを考えます。

```c
struct {
    int timestamp;
    float value1;
    float value2;
}
```

この構造体に対するparserは次の通りです。

`background/parsers/sampleparser.py`

```python
from background.abstractparser import AbstractParser
import struct

class SampleParser(AbstractParser):
    """
    Parser for sample data.
    """
    def __init__(self):
        self.parser=struct.Struct(">Iff")

    @staticmethod
    def get_name() -> str:
        return "sample"

    @staticmethod
    def get_keys() -> list[str]:
        return ["timestamp", "value1", "value2"]

    @staticmethod
    def get_data_length() -> int:
        return 12

    @staticmethod
    def get_id_bytes() -> list[(int, bytes)]:
        return []  # 他のparserと区別する必要がある場合に用います。区別する必要がない場合は、このように空のlistを返すようにしてください。（メソッドを定義しないとエラーになります）

    def parse(self, data: bytes) -> dict:
        if len(data) != self.get_data_length():
            raise ValueError(f"Expected {self.get_data_length()} bytes, got {len(data)} bytes")

        timestamp, value1, value2 = self.parser.unpack(data)
        return {
            "timestamp": timestamp,
            "value1": value1,
            "value2": value2
        }

# 最後にparserという名前のインスタンスを作成しておきます。
# こうすることで、自動的にこのparserを読み込みます。
parser = SampleParser()
```

ポイントは次の通りです。

- `AbstractParser`クラスをimportし、継承してください。このクラスを継承してない場合、実行時エラーになります。
- `get_name()`, `get_keys()`, `get_data_length()`, `get_id_bytes()`, `parse(self, data: bytes)`を定義してください。AbstractParserクラスの中で`abstractMethod`として定義されているため、実装しないと実行時エラーになります。
- `get_name()`メソッドで定義した名前が、parserの名前として扱われます。APIエンドポイントの`parsers`や`parser/<parsername>`などで用いられる名前となります。そのため、**小文字で統一することを推奨します。**
- `get_keys()`メソッドで定義したkeyが、`parser/<parsername>`で帰ってくるkey一覧になります。**`parse()`メソッドでの返り値と異なる値でも定義できてしまうため、実装には十分気をつけてください。**
- `get_data_length()`で定義した値と`get_id_bytes()`で定義した値に一致するデータのみがparseされます。こちらも**parse()メソッドの実装と異なる値でも定義できてしまうため、実装時には注意するようにしてください。**
- `get_id_bytes()`メソッドは、`(bytesの中の開始インデックス(int), 実際にきて欲しい値(bytes))`の配列を返すように実装します。例えば、先頭に必ず0x10が来て、さらに10個目と11個目に`0xA0`,`0xB0`ときて欲しい場合は
  ```python
  return [(0, b'\x10'), (10, b'\xA0\xB0')]
  ```
  というふうに記述します。この機能は、正しいデータが来ているかどうか確かめるためと、parserが複数ある場合にどのparserを用いるべきか判別するために用いられます。
- 複数のparserを用いる場合は`get_id_bytes()`と`get_id_bytes()`でただ1つのparserのみが条件にあうようにしてください。
- `parse()`メソッドはbytes型を受け取りdictとして値を返すような実装になっていれば、中身をどう書いても構いません。上の例ではstructモジュールを用いていますが、bytesから直接読み取るなどの実装を行ってもらっても大丈夫です。

これらのことを守って`parser`を定義すれば、対応するデータがきたときに自動的にparseしてくれます。
