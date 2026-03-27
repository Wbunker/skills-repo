# Java 11 Security
## TLS 1.3, ChaCha20-Poly1305, Curve25519/448, JSSE, java.security API

---

## TLS 1.3 (JEP 332)

Java 11 implements TLS 1.3 (RFC 8446), the most significant TLS update in years.

### Key Improvements over TLS 1.2

| Feature | TLS 1.2 | TLS 1.3 |
|---------|---------|---------|
| Handshake round-trips | 2 RTT | 1 RTT (0-RTT session resumption) |
| Forward secrecy | Optional | Mandatory (ephemeral keys always) |
| Cipher suites | 37+ (many weak) | 5 (all strong) |
| Removed algorithms | Still present | RSA key exchange, SHA-1 signing, RC4, 3DES removed |
| Session resumption | Session ID / tickets | PSK (Pre-Shared Keys) |

### Enabling TLS 1.3

TLS 1.3 is **enabled by default** in Java 11. The `SSLContext` negotiates TLS 1.3 automatically when both sides support it.

```java
// Default SSLContext — TLS 1.3 negotiated automatically
SSLContext ctx = SSLContext.getDefault();

// Explicit TLS 1.3
SSLContext ctx = SSLContext.getInstance("TLSv1.3");
ctx.init(keyManagers, trustManagers, new SecureRandom());

// With HttpClient
HttpClient client = HttpClient.newBuilder()
    .sslContext(ctx)
    .build();
```

### Supported Cipher Suites (TLS 1.3)

```
TLS_AES_128_GCM_SHA256
TLS_AES_256_GCM_SHA384
TLS_CHACHA20_POLY1305_SHA256
TLS_AES_128_CCM_SHA256
TLS_AES_128_CCM_8_SHA256
```

### Restrict to TLS 1.3 Only

```java
SSLSocket socket = (SSLSocket) factory.createSocket(host, port);
socket.setEnabledProtocols(new String[]{"TLSv1.3"});
```

---

## ChaCha20 and Poly1305 (JEP 329)

Java 11 adds ChaCha20 stream cipher and Poly1305 authenticator (RFC 7539/8439).

**Why ChaCha20?** AES-GCM is fast with hardware AES-NI support, but ChaCha20 is faster in software (mobile devices, older hardware without AES-NI).

### ChaCha20 Encryption

```java
import javax.crypto.*;
import javax.crypto.spec.*;
import java.security.*;

// Generate key (256-bit)
KeyGenerator keyGen = KeyGenerator.getInstance("ChaCha20");
keyGen.init(256);
SecretKey key = keyGen.generateKey();

// 12-byte nonce (96-bit) — must be unique per encryption with same key
byte[] nonce = new byte[12];
new SecureRandom().nextBytes(nonce);

// Counter = 1 (required for ChaCha20-Poly1305)
ChaCha20ParameterSpec spec = new ChaCha20ParameterSpec(nonce, 1);

Cipher cipher = Cipher.getInstance("ChaCha20");
cipher.init(Cipher.ENCRYPT_MODE, key, spec);
byte[] ciphertext = cipher.doFinal(plaintext);
```

### ChaCha20-Poly1305 (AEAD — Authenticated Encryption)

```java
// ChaCha20-Poly1305: encryption + authentication in one pass
Cipher aeadCipher = Cipher.getInstance("ChaCha20-Poly1305");

IvParameterSpec iv = new IvParameterSpec(nonce);   // 12-byte nonce
aeadCipher.init(Cipher.ENCRYPT_MODE, key, iv);
// Optional: additional authenticated data (AAD)
aeadCipher.updateAAD(aad);
byte[] ciphertextWithTag = aeadCipher.doFinal(plaintext);
// Output = ciphertext + 16-byte Poly1305 authentication tag
```

---

## Curve25519 and Curve448 Key Agreement (JEP 324)

Java 11 adds Curve25519 (X25519) and Curve448 (X448) Diffie-Hellman key agreement, providing faster and more secure ECDH alternatives.

| Algorithm | Security (bits) | Speed |
|-----------|----------------|-------|
| X25519 | ~128-bit | Very fast |
| X448 | ~224-bit | Moderate |
| ECDH P-256 | ~128-bit | Slower (requires complex curve arithmetic) |

```java
import java.security.*;
import javax.crypto.*;

// X25519 key pair generation
KeyPairGenerator kpg = KeyPairGenerator.getInstance("X25519");
KeyPair keyPairA = kpg.generateKeyPair();
KeyPair keyPairB = kpg.generateKeyPair();

// Key agreement (Diffie-Hellman)
KeyAgreement ka = KeyAgreement.getInstance("X25519");
ka.init(keyPairA.getPrivate());
ka.doPhase(keyPairB.getPublic(), true);
byte[] sharedSecret = ka.generateSecret();

// X448 variant
KeyPairGenerator kpg448 = KeyPairGenerator.getInstance("X448");
KeyPair pair = kpg448.generateKeyPair();
```

---

## `java.security` Core API

### `MessageDigest` — Hashing

```java
MessageDigest md = MessageDigest.getInstance("SHA-256");
byte[] hash = md.digest("hello".getBytes(StandardCharsets.UTF_8));

// Hex encode
String hex = HexFormat.of().formatHex(hash);   // Java 17+
// Java 11 hex encoding:
StringBuilder sb = new StringBuilder();
for (byte b : hash) sb.append(String.format("%02x", b));
```

Supported algorithms: `SHA-256`, `SHA-384`, `SHA-512`, `SHA-512/256`, `SHA3-256`, `SHA3-512`, `MD5` (legacy, insecure).

### `SecureRandom` — Cryptographic Randomness

```java
SecureRandom random = new SecureRandom();
byte[] bytes = new byte[32];
random.nextBytes(bytes);

// Specific algorithm
SecureRandom drbg = SecureRandom.getInstance("DRBG");
```

### `KeyStore` — Certificate and Key Storage

```java
KeyStore ks = KeyStore.getInstance("PKCS12");
try (InputStream is = new FileInputStream("keystore.p12")) {
    ks.load(is, password);
}

// Get private key
PrivateKey key = (PrivateKey) ks.getKey("alias", keyPassword);
// Get certificate
X509Certificate cert = (X509Certificate) ks.getCertificate("alias");
```

### `Cipher` — Symmetric Encryption

```java
// AES-GCM (recommended symmetric encryption)
KeyGenerator kg = KeyGenerator.getInstance("AES");
kg.init(256);
SecretKey aesKey = kg.generateKey();

byte[] iv = new byte[12];
new SecureRandom().nextBytes(iv);
GCMParameterSpec gcmSpec = new GCMParameterSpec(128, iv);  // 128-bit auth tag

Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
cipher.init(Cipher.ENCRYPT_MODE, aesKey, gcmSpec);
byte[] encrypted = cipher.doFinal(plaintext);

// Decrypt
cipher.init(Cipher.DECRYPT_MODE, aesKey, gcmSpec);
byte[] decrypted = cipher.doFinal(encrypted);
```

### `KeyPairGenerator` — Asymmetric Keys

```java
// RSA
KeyPairGenerator rsa = KeyPairGenerator.getInstance("RSA");
rsa.initialize(2048);
KeyPair rsaKeys = rsa.generateKeyPair();

// EC (Elliptic Curve)
KeyPairGenerator ec = KeyPairGenerator.getInstance("EC");
ec.initialize(new ECGenParameterSpec("secp256r1"));
KeyPair ecKeys = ec.generateKeyPair();
```

### `Signature` — Digital Signatures

```java
// Sign
Signature signer = Signature.getInstance("SHA256withRSA");
signer.initSign(privateKey);
signer.update(data);
byte[] sig = signer.sign();

// Verify
Signature verifier = Signature.getInstance("SHA256withRSA");
verifier.initVerify(publicKey);
verifier.update(data);
boolean valid = verifier.verify(sig);
```

### `Mac` — Message Authentication Code

```java
Mac mac = Mac.getInstance("HmacSHA256");
SecretKeySpec hmacKey = new SecretKeySpec(keyBytes, "HmacSHA256");
mac.init(hmacKey);
byte[] tag = mac.doFinal(message);
```

---

## JSSE — Java Secure Socket Extension

### SSLContext Configuration

```java
// Load trust store
TrustManagerFactory tmf = TrustManagerFactory.getInstance(
    TrustManagerFactory.getDefaultAlgorithm());
KeyStore trustStore = KeyStore.getInstance("PKCS12");
trustStore.load(trustStoreStream, trustStorePassword);
tmf.init(trustStore);

// Load key store (for mutual TLS / client auth)
KeyManagerFactory kmf = KeyManagerFactory.getInstance(
    KeyManagerFactory.getDefaultAlgorithm());
KeyStore keyStore = KeyStore.getInstance("PKCS12");
keyStore.load(keyStoreStream, keyStorePassword);
kmf.init(keyStore, keyPassword);

// Build SSLContext
SSLContext ctx = SSLContext.getInstance("TLS");
ctx.init(kmf.getKeyManagers(), tmf.getTrustManagers(), new SecureRandom());
```

### SSLSocket (Low-Level)

```java
SSLSocketFactory factory = ctx.getSocketFactory();
try (SSLSocket socket = (SSLSocket) factory.createSocket("example.com", 443)) {
    socket.setEnabledProtocols(new String[]{"TLSv1.2", "TLSv1.3"});
    socket.startHandshake();
    // Use socket.getInputStream() / getOutputStream()
}
```

---

## Security Best Practices

### Passwords

```java
// Use char[] for passwords — can be zeroed after use
char[] password = readPassword();
try {
    // use password
} finally {
    Arrays.fill(password, '\0');  // wipe from memory
}

// Hash passwords with bcrypt/scrypt/Argon2 (not built into Java — use a library)
// java.security MessageDigest is NOT suitable for password storage
```

### Secure Coding Rules

| Rule | Reason |
|------|--------|
| Use `SecureRandom`, not `Random` | `Random` is predictable |
| Use AES-GCM, not AES-ECB | ECB reveals patterns in plaintext |
| Use SHA-256+, not MD5/SHA-1 | MD5/SHA-1 are broken for collision resistance |
| Validate all inputs before processing | Injection, overflow, format attacks |
| Use `PreparedStatement` for SQL | Prevents SQL injection |
| Zero sensitive arrays after use | `Arrays.fill(bytes, (byte)0)` |
| Never log passwords, keys, secrets | Log sanitization |
| Use HTTPS everywhere | Man-in-the-middle protection |

### `SecurityManager` (Java 11 — Available; Deprecated Java 17)

Still present in Java 11 but deprecated in Java 17:

```java
System.setSecurityManager(new SecurityManager());
// Use SecurityManager.checkRead(), checkWrite(), etc.
```

---

## Kerberos 5 AES Encryption (RFC 8009)

Java 11 adds AES-128 and AES-256 with SHA-256 and SHA-384 HMAC for Kerberos 5 (RFC 8009). Configured via `krb5.conf`. No code changes needed — handled by GSSAPI/JAAS layer.
