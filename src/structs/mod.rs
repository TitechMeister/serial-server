use serde::{Deserialize, Serialize};

#[derive(Clone)]
pub enum SensorData {
    Ultrasonic(UltrasonicData),
    Barometer(BarometerData),
}

#[derive(Serialize, Deserialize, Debug, PartialEq, Clone)]
pub enum DataType {
    MainBoard = 0x00, // メイン基板

    ServoController = 0x10, // 操舵基板

    Tachometer = 0x20, // 回転出力計

    Thrustmeter = 0x21, //推力計

    Pitot = 0x30, // ピトー管

    IMU = 0x40, // IMU

    Ultrasonic = 0x50, // 超音波式高度計

    GPS = 0x60, // GPS

    Vane = 0x70, // 風見

    Barometer = 0x90 // 気圧計
}

#[derive(Serialize, Deserialize, Debug, PartialEq, Clone)]
pub struct UltrasonicRawData {
    pub id: u8,
    pub timestamp: u32,
    pub altitude: f32,
    pub temperature: f32,
    pub received_time: i64
}

#[derive(Debug, PartialEq, Clone)]
pub struct UltrasonicData {
    pub id: DataType,
    pub raw: UltrasonicRawData,
}

impl UltrasonicData {
    pub fn new(id: u8, timestamp: u32, altitude: f32, temperature: f32, received_time: i64) -> Self {
        let raw = UltrasonicRawData {
            id,
            timestamp,
            altitude,
            temperature,
            received_time
        };
        UltrasonicData { id: DataType::Ultrasonic, raw }
    }

    pub fn parse(data: Vec<u8>) -> Option<Self> {
        if data.len() < 5 {
            eprintln!("Invalid data length");
            return None;
        }

        let id = data[0];
        let timestamp = u32::from_le_bytes([data[4], data[5], data[6], data[7]]);
        let altitude = f32::from_le_bytes([data[8], data[9], data[10], data[11]]);
        let temperature = f32::from_le_bytes([data[12], data[13], data[14], data[15]]);
        let received_time = chrono::Utc::now().timestamp_millis();
        if (id != DataType::Ultrasonic as u8) {
            eprintln!("Invalid data type for Ultrasonic: {}", id);
            return None;
        } else {
            Some(UltrasonicData::new(id, timestamp, altitude, temperature, received_time))
        }
    }
}

#[derive(Serialize, Deserialize, Debug, PartialEq, Clone)]
pub struct BarometerRawData {
    pub id: u8,
    pub timestamp: u32,
    pub pressure: f32,
    pub temperature: f32,
    pub received_time: i64
}

#[derive(Debug, PartialEq, Clone)]
pub struct BarometerData {
    pub id: DataType,
    pub raw: BarometerRawData,
}

impl BarometerData {
    pub fn new(id: u8, timestamp: u32, pressure: f32, temperature: f32, received_time: i64) -> Self {
        BarometerData {
            id: DataType::Barometer,
            raw: BarometerRawData {
                id,
                timestamp,
                pressure,
                temperature,
                received_time
            }
        }
    }

    pub fn parse(data: Vec<u8>) -> Option<Self> {
        if data.len() < 5 {
            eprintln!("Invalid data length");
            return None;
        }

        let id = data[0];
        let timestamp = u32::from_le_bytes([data[4], data[5], data[6], data[7]]);
        let pressure = f32::from_le_bytes([data[8], data[9], data[10], data[11]]);
        let temperature = f32::from_le_bytes([data[12], data[13], data[14], data[15]]);
        let received_time = chrono::Utc::now().timestamp_millis();
        if id != DataType::Barometer as u8 {
            eprintln!("Invalid data type for Barometer: {}", id);
            return None;
        } else {
            Some(BarometerData::new(id, timestamp, pressure, temperature, received_time))
        }
    }
}