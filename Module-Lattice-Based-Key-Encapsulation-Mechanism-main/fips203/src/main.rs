use fips203::ml_kem_512;
use fips203::traits::{KeyGen, Encaps, Decaps, SerDes};

use aes_gcm::{Aes256Gcm, Nonce};
use aes_gcm::aead::{Aead, KeyInit};
use aes_gcm::aead::generic_array::GenericArray;

use sha3::{Shake256, digest::{Update, ExtendableOutput, XofReader}};
use rand::RngCore;
use hex;

fn derive_aes_key(shared_secret: &[u8]) -> [u8; 32] {
    let mut hasher = Shake256::default();
    hasher.update(shared_secret);
    let mut reader = hasher.finalize_xof();
    let mut key = [0u8; 32];
    reader.read(&mut key);
    key
}

fn main() {

    let (alice_ek, alice_dk) = ml_kem_512::KG::try_keygen().unwrap();

    
    let alice_ek_bytes = alice_ek.into_bytes();

    
    let bob_ek = ml_kem_512::EncapsKey::try_from_bytes(alice_ek_bytes).unwrap();
    let (bob_ssk_bytes, bob_ct) = bob_ek.try_encaps().unwrap();
    let bob_ct_bytes = bob_ct.into_bytes();

    
    let alice_ct = ml_kem_512::CipherText::try_from_bytes(bob_ct_bytes).unwrap();
    let alice_ssk_bytes = alice_dk.try_decaps(&alice_ct).unwrap();

    assert_eq!(bob_ssk_bytes, alice_ssk_bytes);
    println!("Shared secret established.");
    

    let bob_ssk_array = bob_ssk_bytes.into_bytes();


    let aes_key = derive_aes_key(&bob_ssk_array);

    
    let key = GenericArray::from_slice(&aes_key);
    let cipher = Aes256Gcm::new(key);

    
    let mut nonce_bytes = [0u8; 12];
    rand::thread_rng().fill_bytes(&mut nonce_bytes);
    let nonce = Nonce::from_slice(&nonce_bytes);

    
    let plaintext = b"Hello, world!";
    println!("Plaintext: {}", String::from_utf8_lossy(plaintext));

    let ciphertext = cipher.encrypt(nonce, plaintext.as_ref()).expect("encryption failure!");
    println!("Ciphertext (hex): {}", hex::encode(&ciphertext));

    
    let decrypted_plaintext = cipher.decrypt(nonce, ciphertext.as_ref()).expect("decryption failure!");
    println!("Decrypted text: {}", String::from_utf8_lossy(&decrypted_plaintext));


    assert_eq!(plaintext, decrypted_plaintext.as_slice());
    println!(" Decryption successful, message integrity verified.");
}
