# serial-server

An application that outputs input from a serial port as an HTTP server.

## Usage

For standart use

```shell
$ cargo run
```

If you want to decode serialport inputs in a specific way, please run as below.

```shell
$ cargo run -- -e {encode-type}
```

You can currently choose

- COBS
- CRLF (store inputs to buffer until '\n' received)
