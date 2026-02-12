#!/bin/bash

# Let's Encrypt SSL Certificate Initialization Script for maiorbicho.com
# This script automates the first-time SSL certificate generation

set -e

# Hardcoded domains - NO NEED TO EDIT THESE
domains=(maiorbicho.com www.maiorbicho.com)
rsa_key_size=4096
data_path="./certbot"
email="admin@maiorbicho.com"  # Change this if needed
staging=0  # Set to 1 if you're testing your setup to avoid hitting request limits

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[SETUP]${NC} $1"
}

# Check if domain resolves to current IP (optional warning)
check_domain_resolution() {
    print_header "Checking domain resolution..."
    
    # Get current public IP
    current_ip=$(curl -s ifconfig.me || curl -s ipinfo.io/ip || echo "unknown")
    
    if [ "$current_ip" != "unknown" ]; then
        for domain in "${domains[@]}"; do
            domain_ip=$(dig +short $domain | head -n1)
            if [ -n "$domain_ip" ] && [ "$domain_ip" != "$current_ip" ]; then
                print_warning "Domain $domain resolves to $domain_ip but current IP is $current_ip"
                print_warning "Make sure DNS is properly configured before running this script"
                echo
            elif [ -n "$domain_ip" ]; then
                print_status "Domain $domain correctly resolves to $current_ip"
            else
                print_warning "Could not resolve domain $domain"
            fi
        done
    else
        print_warning "Could not determine current IP address"
    fi
    echo
}

# Download recommended TLS parameters
download_ssl_params() {
    print_header "Downloading recommended TLS parameters..."
    
    if [ ! -e "$data_path/conf/options-ssl-nginx.conf" ] || [ ! -e "$data_path/conf/ssl-dhparams.pem" ]; then
        print_status "Creating directories..."
        mkdir -p "$data_path/conf"
        
        print_status "Downloading SSL parameters..."
        curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "$data_path/conf/options-ssl-nginx.conf"
        curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/ssl-dhparams.pem > "$data_path/conf/ssl-dhparams.pem"
        
        print_status "TLS parameters downloaded successfully"
    else
        print_status "TLS parameters already exist, skipping download"
    fi
    echo
}

# Create dummy certificates
create_dummy_certificates() {
    print_header "Phase 1: Creating dummy certificates..."
    
    if [ -d "$data_path/conf/live/$domain" ]; then
        print_warning "Certificate directory already exists for $domain"
        read -p "Do you want to continue and replace existing certificates? (y/N) " decision
        if [ "$decision" != "Y" ] && [ "$decision" != "y" ]; then
            print_status "Certificate generation cancelled"
            exit 0
        fi
    fi
    
    print_status "Creating directories for dummy certificates..."
    path="/etc/letsencrypt/live/$domains"
    mkdir -p "$data_path/conf/live/$domains"
    
    print_status "Generating dummy RSA key..."
    openssl genrsa -out "$data_path/conf/live/$domains/privkey.pem" $rsa_key_size
    
    print_status "Generating dummy certificate..."
    openssl req -new -key "$data_path/conf/live/$domains/privkey.pem" \
        -out "$data_path/conf/live/$domains/cert.csr" \
        -subj "/CN=$domains"
    
    openssl x509 -req -days 1 \
        -in "$data_path/conf/live/$domains/cert.csr" \
        -signkey "$data_path/conf/live/$domains/privkey.pem" \
        -out "$data_path/conf/live/$domains/fullchain.pem"
    
    print_status "Dummy certificates created successfully"
    echo
}

# Start nginx
start_nginx() {
    print_header "Phase 2: Starting Nginx with dummy certificates..."
    
    # Copy SSL params to nginx directory
    mkdir -p ./nginx
    cp "$data_path/conf/options-ssl-nginx.conf" ./nginx/
    
    # Start nginx
    docker-compose up -d nginx
    
    print_status "Waiting for Nginx to start..."
    sleep 10
    
    # Check if nginx is running
    if docker-compose ps nginx | grep -q "Up"; then
        print_status "Nginx started successfully"
    else
        print_error "Failed to start Nginx"
        docker-compose logs nginx
        exit 1
    fi
    echo
}

# Remove dummy certificates and request real ones
request_real_certificates() {
    print_header "Phase 3: Requesting real Let's Encrypt certificates..."
    
    # Remove dummy certificates
    print_status "Removing dummy certificates..."
    rm -rf "$data_path/conf/live/$domains"
    
    # Build domain arguments for certbot
    domain_args=""
    for domain in "${domains[@]}"; do
        domain_args="$domain_args -d $domain"
    done
    
    # Choose staging or production
    if [ $staging != "0" ]; then
        staging_arg="--staging"
        print_warning "Using staging environment for testing"
    else
        staging_arg=""
        print_status "Using production environment"
    fi
    
    print_status "Requesting certificates for: ${domains[*]}"
    
    # Request certificates
    docker-compose run --rm --entrypoint "\
        certbot certonly --webroot --webroot-path=/var/www/certbot \
            $staging_arg \
            --email $email \
            --rsa-key-size $rsa_key_size \
            --agree-tos \
            --force-renewal \
            $domain_args" certbot
    
    print_status "Certificate request completed"
    echo
}

# Reload nginx with real certificates
reload_nginx() {
    print_header "Phase 4: Reloading Nginx with real certificates..."
    
    # Check if certificates were created
    if [ -f "$data_path/conf/live/$domains/fullchain.pem" ]; then
        print_status "Real certificates found!"
        
        # Reload nginx
        print_status "Reloading Nginx..."
        docker-compose exec nginx nginx -s reload
        
        print_status "Nginx reloaded successfully with real certificates"
        
        # Show certificate info
        print_status "Certificate information:"
        docker-compose run --rm certbot certificates
        
    else
        print_error "Failed to create SSL certificates"
        print_error "Please check the logs above and try again"
        docker-compose logs certbot
        exit 1
    fi
    echo
}

# Final verification
verify_setup() {
    print_header "Final verification..."
    
    print_status "Checking certificate files..."
    if [ -f "$data_path/conf/live/$domains/fullchain.pem" ] && [ -f "$data_path/conf/live/$domains/privkey.pem" ]; then
        print_status "✓ Certificate files exist"
    else
        print_error "✗ Certificate files missing"
        return 1
    fi
    
    print_status "Checking Nginx configuration..."
    if docker-compose exec nginx nginx -t > /dev/null 2>&1; then
        print_status "✓ Nginx configuration is valid"
    else
        print_error "✗ Nginx configuration error"
        docker-compose exec nginx nginx -t
        return 1
    fi
    
    print_status "Checking service status..."
    if docker-compose ps | grep -q "Up"; then
        print_status "✓ Services are running"
    else
        print_error "✗ Some services are not running"
        docker-compose ps
        return 1
    fi
    
    print_status "✓ Setup verification completed successfully"
    echo
}

# Main execution
main() {
    print_header "Starting SSL certificate initialization for maiorbicho.com"
    echo
    
    # Check prerequisites
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        print_warning ".env file not found, creating from .env.example"
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_status "Please edit .env file with your actual values before continuing"
            exit 1
        else
            print_error ".env.example file not found"
            exit 1
        fi
    fi
    
    # Execute phases
    check_domain_resolution
    download_ssl_params
    create_dummy_certificates
    start_nginx
    request_real_certificates
    reload_nginx
    verify_setup
    
    # Success message
    print_header "🎉 Setup completed successfully!"
    echo
    print_status "Your site should now be accessible at:"
    for domain in "${domains[@]}"; do
        echo "  • https://$domain"
    done
    echo
    print_status "Important notes:"
    echo "1. Certificate auto-renewal is configured and will run every 12 hours"
    echo "2. Make sure ports 80 and 443 are open in your firewall"
    echo "3. Monitor your certificates with: docker-compose logs certbot"
    echo "4. Test your SSL configuration at: https://www.ssllabs.com/ssltest/"
    echo
}

# Run main function
main "$@"
