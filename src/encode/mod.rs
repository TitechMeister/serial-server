#[derive(Debug, PartialEq)]
pub enum EncodeType {
    None,
    COBS,
    CRLF,
}

pub fn print_available_encodings() {
    println!("Available encodings:");
    println!("1. None (default)");
    println!("2. COBS");
    println!("3. CRLF (store inputs until a newline is received)");
}