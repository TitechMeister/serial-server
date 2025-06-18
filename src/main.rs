use std::io::{stdin, stdout, Write};
use std::sync::mpsc;
use std::net::TcpListener;

use serial_server::encode::{self, EncodeType};
use serialport::SerialPort;
fn main() {
    let mut encode_type: EncodeType = EncodeType::CRLF; // Default encoding type
    let args: Vec<String> = std::env::args().collect();
    println!("{:?}", args);
    if args.len() > 1 {
        if args[1].starts_with("-h") || args[1].starts_with("--help") {
            println!("Usage: {} [options]", args[0]);
            println!("Options:");
            println!("  -h, --help       Show this help message");
            println!("  -e, --encode     Encode types");
            return;
        }
        if args[1].starts_with("-e") {
            if args.len() > 2 {
                if args[2] == "COBS" {
                    encode_type = EncodeType::COBS;
                    println!("Encoding type set to COBS");
                } else if args[2] == "CRLF" {
                    encode_type = EncodeType::CRLF;
                    println!("Encoding type set to CRLF");
                } else {
                    println!("Unknown encoding type. Please set one of the following:");
                    encode::print_available_encodings();
                }
            } else {
                println!("No encoding type specified. Please set one of the following:");
                encode::print_available_encodings();
                return;
            }
        }
    }

    let mut port = match port_search() {
        Some(port) => port,
        None => {
            return;
        }
    };

    let (tx, rx) = mpsc::channel::<Vec<u8>>();
    // Start a new thread to handle the port session
    let port_thread = std::thread::spawn(move || {
        port_session(port.as_mut(), tx, encode_type);
    });
    let server_thread = std::thread::spawn(move || {
        server_session(rx);
    });

    // Wait for the threads to finish
    port_thread.join().expect("Port thread panicked");
    server_thread.join().expect("Server thread panicked");
}

/// Returns the name of a serial port to connect to.
///  If no port is found, it returns an empty string.
fn port_search() -> Option<Box<dyn serialport::SerialPort>> {
    let ports = serialport::available_ports().expect("No ports found!");
    
    println!("Ports:");
    for port in ports.iter() {
        println!("{}, {:?}", port.port_name, port.port_type);
    }

    let mut input = String::new();

    println!("Please enter the port name to connect to:");
    stdin()
        .read_line(&mut input)
        .expect("Failed to read line");

    println!("Searching for port: {}", input.trim());

    for port in ports.iter() {
        if port.port_name.contains(input.trim()) {
            println!("port found: {}, {:?}", port.port_name, port.port_type);

            print!("Do you want to connect to? (y/n): ");
            stdout().flush().expect("Failed to flush stdout");
            let mut input = String::new();
            stdin().read_line(&mut input).expect("Failed to read line");
            let response = input.trim();

            if response.eq_ignore_ascii_case("y") || response.eq_ignore_ascii_case("yes") {
                // ここでポートへの接続処理を行う
                print!("please input baud rate: ");
                stdout().flush().expect("Failed to flush stdout");
                let mut input = String::new();
                stdin().read_line(&mut input).expect("Failed to read line");
                let baud_rate = input.trim().parse::<u32>().expect("Invalid baud rate");
                let connect_port = serialport::new(port.port_name.clone(), baud_rate)
                    .open()
                    .expect("Failed to open port");

                println!("Connected to port: {}", port.port_name);
                println!("You can now communicate with the device connected to the port.");
                return Some(connect_port);
            } else {
                println!("Connection cancelled. Searching for another port...");
            }
        }
    }
    println!("Port not found.");
    return None
}


/// Handles the session with the specified port.
///
fn port_session(port: &mut dyn SerialPort, tx: mpsc::Sender<Vec<u8>>, encode_type: EncodeType) {
    let mut buffer: [u8; 1024] = [0; 1024];
    let mut buffer_index = 0;
    loop {
        // ここでポートからの応答を読み取る処理を行う
        let mut read_buf: [u8; 1024] = [0; 1024];
        match port.read(&mut read_buf) {
            Ok(bytes_read) => {
                match encode_type {
                    EncodeType::COBS => {
                        // COBSエンコードの場合の処理
                        for i in 0..bytes_read {
                            buffer[buffer_index] = read_buf[i];
                            buffer_index += 1;
                            if read_buf[i] == 0 {
                                // COBSエンコードの終了条件
                                let mut decoded_data: [u8; 1024] = [0; 1024];
                                match cobs::decode(&buffer[..buffer_index], &mut decoded_data) {
                                    Ok(decoded_length) => {
                                        // デコードされたデータを送信
                                        tx.send(decoded_data[..decoded_length].to_vec())
                                            .expect("Failed to send data through channel");
                                        buffer_index = 0; // バッファをリセット
                                    }
                                    Err(e) => {
                                        eprintln!("COBS decode error: {}", e);
                                    }
                                };
                            }
                            if buffer_index >= buffer.len() {
                                // バッファがいっぱいになった場合はリセット
                                eprintln!("Buffer overflow, resetting buffer.");
                                tx.send(buffer[..buffer_index].to_vec())
                                    .expect("Failed to send data through channel");
                                buffer_index = 0;
                            }
                        }
                    }
                    EncodeType::CRLF => {
                        for i in 0..bytes_read {
                            buffer[buffer_index] = read_buf[i];
                            buffer_index += 1;
                            if read_buf[i] == b'\n' {
                                // CRLFエンコードの終了条件
                                tx.send(buffer[..buffer_index].to_vec())
                                    .expect("Failed to send data through channel");
                                buffer_index = 0; // バッファをリセット
                            }
                            if buffer_index >= buffer.len() {
                                // バッファがいっぱいになった場合はリセット
                                eprintln!("Buffer overflow, resetting buffer.");
                                tx.send(buffer[..buffer_index].to_vec())
                                    .expect("Failed to send data through channel");
                                buffer_index = 0;
                            }
                        }
                    }
                }
            }
            Err(e) => {
                if e.kind() == std::io::ErrorKind::TimedOut {
                    // タイムアウトエラーは無視
                    continue;
                } else {
                    // その他のエラーは表示
                eprintln!("Failed to read from port: {}", e);
                }
            }
        }
    }
}

fn server_session(rx: mpsc::Receiver<Vec<u8>>) {
    // ここでサーバーセッションの処理を行う
    // 例えば、クライアントからの接続を待ち受けるなど
    println!("Server session started.");

    let listener = TcpListener::bind("127.0.0.1:8080")
        .expect("Failed to bind to address");

    for stream in listener.incoming() {
        let (tx_client, rx_client) = mpsc::channel::<Vec<u8>>();
        match stream {
            Ok(stream) => {
                println!("Client connected: {}", stream.peer_addr().unwrap());
                // クライアントとの通信を処理する
                std::thread::spawn(move || {
                    handle_client(stream, rx_client);
                });
                tx_client.send(rx.recv().expect("Failed to receive data from channel"))
                    .expect("Failed to send data to client");
            }
            Err(e) => {
                eprintln!("Failed to accept connection: {}", e);
            }
        }
    }


    loop {
        match rx.recv() {
            Ok(data) => {
                // 受信したデータを処理する
                println!("Received data: {:?}", data);
            }
            Err(e) => {
                eprintln!("Failed to receive data: {}", e);
                break; // エラーが発生した場合はループを抜ける
            }
        }
    }
}

fn handle_client(mut stream: std::net::TcpStream, rx: mpsc::Receiver<Vec<u8>>) {
    println!("Handling client: {}", stream.peer_addr().unwrap());
    loop {
        match rx.recv() {
            Ok(data) => {
                // クライアントにデータを送信
                if let Err(e) = stream.write_all(&data) {
                    eprintln!("Failed to write to client: {}", e);
                    break; // エラーが発生した場合はループを抜ける
                }
                println!("Sent data to client: {:?}", data);
            }
            Err(e) => {
                eprintln!("Failed to receive data from channel: {}", e);
                break; // エラーが発生した場合はループを抜ける
            }
        }
    }
}