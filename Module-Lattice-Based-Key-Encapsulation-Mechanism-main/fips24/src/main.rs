use fips204::ml_dsa_44; 
use fips204::traits::{Signer, Verifier};

use hex;

fn main() {
    let (pk, sk) = match ml_dsa_44::try_keygen() {
        Ok(keys) => keys,
        Err(e) => {
            eprintln!("Key generation failed: {e}");
            return;
        }
    };
    println!("Keypair generated successfully.");
    let message = b"Hello, world!";
    println!("Message: \"{}\"", String::from_utf8_lossy(message));

    let signature = match sk.try_sign(message, &[]) {
        Ok(sig) => sig,
        Err(e) => {
            eprintln!("Signing failed: {e}");
            return;
        }
    };
    println!("Signature (hex): {}", hex::encode(&signature));

    let verified = pk.verify(message, &signature, &[]);
    if verified {
        println!("Signature verified successfully!");
    } else {
        println!("Signature verification failed.");
    }
}
