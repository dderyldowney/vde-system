# Predefined VM Types

All available programming languages and services that can be created with VDE.

[← Back to README](../README.md)

---

## Language VMs (19 total, ports 2200-2299)

| Name | Aliases | Display Name | Container Name | SSH Host | Install Command |
|------|---------|--------------|----------------|----------|-----------------|
| c | c | C | vde-c | vde-c | gcc, make, cmake, gdb |
| cpp | c++, gcc | C++ | vde-cpp | vde-cpp | g++, make, cmake, gdb |
| asm | assembler, nasm | Assembler | vde-asm | vde-asm | nasm, yasm, gdb |
| python | python3 | Python | vde-python | vde-python | python3, python3-pip |
| rust | rust | Rust | vde-rust | vde-rust | rustup (via install script) |
| js | node, nodejs | JavaScript | vde-js | vde-js | Node.js LTS |
| csharp | dotnet | C# | vde-csharp | vde-csharp | dotnet-sdk-8.0 |
| ruby | ruby | Ruby | vde-ruby | vde-ruby | ruby-full |
| go | golang | Go | vde-go | vde-go | golang-go |
| java | jdk | Java | vde-java | vde-java | default-jdk, maven, gradle |
| kotlin | kotlin | Kotlin | vde-kotlin | vde-kotlin | kotlin, SDKMAN |
| swift | swift | Swift | vde-swift | vde-swift | binutils, git, libc6-dev, curl |
| php | php | PHP | vde-php | vde-php | php, php-cli, composer |
| scala | scala | Scala | vde-scala | vde-scala | scala-defaults, sbt |
| r | rlang, r | R | vde-r | vde-r | r-base, r-cran-littler |
| lua | lua | Lua | vde-lua | vde-lua | lua5.4, luarocks |
| flutter | dart, flutter | Flutter | vde-flutter | vde-flutter | flutter SDK |
| elixir | elixir | Elixir | vde-elixir | vde-elixir | elixir, erlang |
| haskell | ghc, haskell | Haskell | vde-haskell | vde-haskell | ghc, cabal-install |

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
