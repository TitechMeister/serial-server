use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug, PartialEq)]
pub struct UltrasonicData {
    pub id: u8,
    pub timestamp: u32,
    pub altitude: f32,
    pub temperature: f32,
    pub received_time: u64
}