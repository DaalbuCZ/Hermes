# SSL Certificates Directory

This directory should contain your SSL certificates for HTTPS support.

## Required Files

- `cert.pem` - SSL certificate (public key)
- `key.pem` - Private key

## Obtaining SSL Certificates

### Option 1: Let's Encrypt (Free)

```bash
# Install certbot
sudo apt-get install certbot

# Generate certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem key.pem
```

### Option 2: Commercial Certificate

1. Purchase SSL certificate from a provider (DigiCert, Comodo, etc.)
2. Download the certificate files
3. Convert to PEM format if necessary
4. Place in this directory

### Option 3: Self-Signed (Development Only)

```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout key.pem -out cert.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

## File Permissions

Ensure proper file permissions:

```bash
chmod 600 key.pem
chmod 644 cert.pem
```

## Renewal

For Let's Encrypt certificates, set up automatic renewal:

```bash
# Test renewal
sudo certbot renew --dry-run

# Add to crontab for automatic renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Security Notes

- Keep private keys secure
- Never commit private keys to version control
- Use strong encryption (RSA 2048+ or ECDSA)
- Regularly update certificates
- Monitor certificate expiration dates
