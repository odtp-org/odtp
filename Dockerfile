# Use Docker in Docker stable version
FROM docker:25.0.3-dind-alpine3.19
ARG PIP_INSTALL_ARGS=

# Install dependencies required
RUN apk add --no-cache \
    gcc \
    libc-dev \
    make \
    openssl-dev \
    libffi-dev \
    zlib-dev \
    git \
    curl \
    wget

# Install Rust and Cargo using rustup (the Rust toolchain installer)
# Note: The following command installs the stable version of Rust and adds Cargo to the PATH
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Install system dependencies required for compiling Fortran and C++ code
# Needed for Numpy.
RUN apk add --no-cache \
    curl \
    gfortran \
    g++ \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Add Cargo to the PATH for the current and future shell sessions
ENV PATH="/root/.cargo/bin:${PATH}"

# Download and install Python 3.11 from source
RUN wget https://www.python.org/ftp/python/3.11.0/Python-3.11.0.tar.xz \
    && tar -xf Python-3.11.0.tar.xz \
    && cd Python-3.11.0 \
    && ./configure --enable-optimizations \
    && make -j `nproc` \
    && make altinstall \
    && ln -s /usr/local/bin/python3.11 /usr/local/bin/python3 \
    && python3 -m ensurepip \
    && python3 -m pip install --upgrade pip setuptools wheel

# Remove the Python source and tarball to reduce image size
RUN rm -rf Python-3.11.0.tar.xz Python-3.11.0

# Install Python and Poetry
RUN python3 -m ensurepip && \
    pip3 install --upgrade pip setuptools

# Install PyArrow in ALPINE
## https://stackoverflow.com/questions/49059779/how-to-install-pyarrow-on-an-alpine-docker-image/53116069#53116069
## https://discuss.streamlit.io/t/anyone-tried-to-install-streamlit-in-alpine-docker-image/56893
RUN apk update && apk add \
    apache-arrow-dev \
    py3-pyarrow \
    && rm -rf /var/lib/apt/lists/*

# Add your application's source code
COPY . /app
WORKDIR /app
RUN pip3 install --upgrade pip && \
    pip3 install --break-system-packages $PIP_INSTALL_ARGS .

# Symbolic link between python and python3
RUN rm /usr/bin/python
RUN ln -s /usr/local/bin/python3 /usr/bin/python

# Entry point in a sh session
ENTRYPOINT ["odtp", "dashboard"]
