# Predefined VM Types

All available programming languages and services that can be created with VDE.

[← Back to README](../README.md)

---

## Language VMs (19 total, ports 2200-2299)

| Name | Aliases | Display Name | Container Name | SSH Host | Install Command |
|------|---------|--------------|----------------|----------|-----------------|
| c | c | C | c-dev | c-dev | gcc, make, cmake, gdb |
| cpp | c++, gcc | C++ | cpp-dev | cpp-dev | g++, make, cmake, gdb |
| asm | assembler, nasm | Assembler | asm-dev | asm-dev | nasm, yasm, gdb |
| python | python3 | Python | python-dev | python-dev | python3, python3-pip |
| rust | rust | Rust | rust-dev | rust-dev | rustup (via install script) |
| js | node, nodejs | JavaScript | js-dev | js-dev | Node.js LTS |
| csharp | dotnet | C# | csharp-dev | csharp-dev | dotnet-sdk-8.0 |
| ruby | ruby | Ruby | ruby-dev | ruby-dev | ruby-full |
| go | golang | Go | go-dev | go-dev | golang-go |
| java | jdk | Java | java-dev | java-dev | default-jdk, maven, gradle |
| kotlin | kotlin | Kotlin | kotlin-dev | kotlin-dev | kotlin, SDKMAN |
| swift | swift | Swift | swift-dev | swift-dev | binutils, git, libc6-dev, curl |
| php | php | PHP | php-dev | php-dev | php, php-cli, composer |
| scala | scala | Scala | scala-dev | scala-dev | scala-defaults, sbt |
| r | rlang, r | R | r-dev | r-dev | r-base, r-cran-littler |
| lua | lua | Lua | lua-dev | lua-dev | lua5.4, luarocks |
| flutter | dart, flutter | Flutter | flutter-dev | flutter-dev | flutter SDK |
| elixir | elixir | Elixir | elixir-dev | elixir-dev | elixir, erlang |
| haskell | ghc, haskell | Haskell | haskell-dev | haskell-dev | ghc, cabal-install |

---

## Service VMs (7 total, ports 2400-2499)

| Name | Aliases | Display Name | Container Name | SSH Host | Service Port | Purpose |
|------|---------|--------------|----------------|----------|--------------|---------|
| postgres | postgresql | PostgreSQL | postgres | postgres | 5432 | PostgreSQL database |
| redis | redis | Redis | redis | redis | 6379 | Key-value store |
| mongodb | mongo | MongoDB | mongodb | mongodb | 27017 | Document database |
| nginx | nginx | Nginx | nginx | nginx | 80, 443 | Web server |
| couchdb | couchdb | CouchDB | couchdb | couchdb | 5984 | NoSQL database |
| mysql | mysql | MySQL | mysql | mysql | 3306 | MySQL database |
| rabbitmq | rabbitmq | RabbitMQ | rabbitmq | rabbitmq | 5672, 15672 | Message queue |

---

## Viewing Available VMs

```bash
# List all VMs (using unified CLI)
vde list

# List only language VMs
vde list --lang
# OR
./scripts/list-vms --lang

# List only service VMs
vde list --svc
# OR
./scripts/list-vms --svc

# Search for specific VMs
vde list python
vde list --lang script
```

---

## Adding New VM Types

See [Extending VDE](./extending-vde.md) for instructions on adding new languages or services.

---

[← Back to README](../README.md)
