#[derive(Debug)]
pub enum EncodeType {
    COBS,
    CRLF,
}

pub fn print_available_encodings() {
    println!("Available encodings:");
    println!("1. COBS (Consistent Overhead Byte Stuffing)");
    println!("2. CRLF (Carriage Return Line Feed)");
}