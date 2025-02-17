FROM python:3.13

COPY ./certs/Zscaler_Root_CA.pem /tmp/Zscaler_Root_CA.pem
# RUN CERT_DIR=$(openssl version -d | cut -f2 -d \")/certs && cp /tmp/Zscaler_Root_CA.pem $CERT_DIR
# RUN update-ca-certificates
# RUN echo "export REQUESTS_CA_BUNDLE=~$CERT_DIR/ca-certificates.pem" >> ~/.bash_profile ; source ~/.bash_profile
# RUN echo "export REQUESTS_CA_BUNDLE=~$CERT_DIR/ca-certificates.pem" >> ~/.bashrc ; source ~/.bash_profile
# Set the working directory

# The following are hard-coded because I'm to dumb to figure out how to set them dynamically (...yet)
ENV CERT_PATH=/usr/lib/ssl/certs/Zscaler_Root_CA.pem
ENV CERT_DIR=/usr/lib/ssl/certs/
ENV SSL_CERT_FILE=${CERT_PATH} 
ENV SSL_CERT_DIR=${CERT_DIR}
ENV REQUESTS_CA_BUNDLE=${CERT_PATH} 

RUN cp /tmp/Zscaler_Root_CA.pem $CERT_DIR
RUN update-ca-certificates

WORKDIR /app

# Copy application code
COPY . .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN ["/bin/bash"]

# Run the application
# CMD ["python", "app/main.py"]
CMD ls -la; sleep infinity