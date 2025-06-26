use core::str;
use std::io::{stdin, stdout, Write};
use std::sync::mpsc;
use std::net::TcpListener;
use actix_web::{get, web, App, HttpResponse, HttpServer, Responder};
use clap::{Parser};
use serde::{Deserialize, Serialize};

use serial_server::encode::{EncodeType};
use serial_server::structs::UltrasonicData;
use serialport::SerialPort;

#[derive(Parser, Debug)]
#[command(next_line_help = true)]
struct Cli {
    /// set encoding type
    /// 
    /// before sending to client, decode input data from serial port.
    /// Available options: None (default), COBS, CRLF
    #[arg(short, long)]
    encode: Option<String>,

    #[arg(short, long, default_value = "log.txt")]
    output: String,
}

#[get("/data/Ultrasonic")]
async fn get_ultrasonic_data() -> impl Responder {
    let ultrasonic_data = UltrasonicData {
        id: 1,
        timestamp: 1234567890,
        altitude: 100.5,
        temperature: 25.0,
        received_time: 1622547800,
    };
    HttpResponse::Ok().json(ultrasonic_data)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let cli = Cli::parse();

    let encode_type: EncodeType = match cli.encode.as_deref() {
        Some("COBS") => EncodeType::COBS,
        Some("CRLF") => EncodeType::CRLF,
        _ => EncodeType::None,
    };
    match encode_type {
        EncodeType::None => {
            println!("Encoding type set to None (default)");
        }
        EncodeType::COBS => {
            println!("Encoding type set to COBS");
        }
        EncodeType::CRLF => {
            println!("Encoding type set to CRLF");
        }
    }

    let mut port = match port_search() {
        Some(port) => port,
        None => {
            panic!("No serial port found. Exiting.");
        }
    };

    let (port_tx, port_rx) = mpsc::channel::<Vec<u8>>();
    // Start a new thread to handle the port session
    let port_thread = std::thread::spawn(move || {
        port_session(port.as_mut(), port_tx, encode_type);
    });
    let server_thread = std::thread::spawn(move || {
        server_session(port_rx);
    });

    HttpServer::new(|| {
        App::new()
            .service(get_ultrasonic_data)
            .route("/", web::get().to(|| async { "Hello, world!" }))
            .route("/port", web::post().to(|| async { "Port session started" }))
    })
    .bind(("127.0.0.1", 7878))?
    .run()
    .await
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
    None
}


/// Handles the session with the specified port.
///
fn port_session(port: &mut dyn SerialPort, tx: mpsc::Sender<Vec<u8>>, encode_type: EncodeType) {
    let mut buffer: [u8; 1024] = [0; 1024];
    let mut buffer_index = 0;

    if encode_type == EncodeType::None {
        port.set_timeout(std::time::Duration::from_secs(1))
            .expect("Failed to set timeout");
    }

    loop {
        // ここでポートからの応答を読み取る処理を行う
        let mut read_buf: [u8; 1024] = [0; 1024];
        match port.read(&mut read_buf) {
            Ok(bytes_read) => {
                match encode_type {
                    EncodeType::None => {
                        // エンコードなしの場合はそのまま送信
                        tx.send(read_buf[..bytes_read].to_vec())
                            .expect("Failed to send data through channel");
                    }
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

fn server_session(port_rx: mpsc::Receiver<Vec<u8>>) {
    // ここでサーバーセッションの処理を行う
    // 例えば、クライアントからの接続を待ち受けるなど
    println!("Server session started.");


    /*
    loop {
        match port_rx.recv() {
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
    */

    let listener = TcpListener::bind("127.0.0.1:8080")
        .expect("Failed to bind to address");

    for stream in listener.incoming() {
        let (tx_client, rx_client) = mpsc::channel::<Vec<u8>>();
        match stream {
            Ok(stream) => {
                println!("Client connected: {}", stream.peer_addr().unwrap());
                // クライアントとの通信を処理する
                std::thread::spawn(move || {
                   // handle_client(stream, rx_client);
                });
                tx_client.send(port_rx.recv().expect("Failed to receive data from channel"))
                    .expect("Failed to send data to client");
            }
            Err(e) => {
                eprintln!("Failed to accept connection: {}", e);
            }
        }
    }
}
