# serial-server

シリアルポートからの入力を読み取り、HTTPサーバーとしてデータをjson形式で出力するプログラムです。
parserを用意することで、バイト列を特定の規則にしたがって整形することができます。

## 使い方

まず、pythonの仮想環境のsetupを行ってください。

```shell
$ source setup.sh
```

アプリの立ち上げ方は次の通りです。

```shell
$ python3 serialserver.py
```

http serverへのアクセス方法は[docs/api.md](docs/api.md)に書いてあります。

また、データparserの追加方法など、詳しい使い方は[docs/usage.md](docs/usage.md)に書いてあります。
