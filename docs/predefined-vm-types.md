# Predefined VM Types

All available programming languages and services that can be created with VDE.

[← Back to README](../README.md)

---

## Language VMs (21 total, ports 2200-2299)

| Name | Aliases | Display Name | Container Name | SSH Port | Install Command |
|------|---------|--------------|----------------|----------|-----------------|
| vde-asm | asm, assembler, nasm | Assembler | vde-asm | 2200 | nasm, yasm, gdb |
| vde-c | c | C | vde-c | 2201 | gcc, make, cmake, gdb |
| vde-cpp | cpp, c++, gcc | C++ | vde-cpp | 2202 | g++, make, cmake, gdb |
| vde-csharp | csharp, dotnet | C# | vde-csharp | 2203 | dotnet-sdk-8.0 |
| vde-displaytest | displaytest | Go Language | vde-displaytest | 2204 | golang-go |
| vde-elixir | elixir, ex, iex | Elixir | vde-elixir | 2205 | elixir, erlang |
| vde-flutter | flutter, dart | Flutter | vde-flutter | 2206 | flutter SDK |
| vde-go | go, golang | Go | vde-go | 2207 | golang-go |
| vde-haskell | haskell, ghc | Haskell | vde-haskell | 2208 | ghc, cabal-install |
| vde-java | java, jdk | Java | vde-java | 2209 | default-jdk, maven, gradle |
| vde-js | js, node, nodejs, npm | Node.js | vde-js | 2210 | Node.js 22.x |
| vde-kotlin | kotlin | Kotlin | vde-kotlin | 2211 | kotlin, SDKMAN |
| vde-lua | lua | Lua | vde-lua | 2212 | lua5.4, luarocks |
| vde-php | php | PHP | vde-php | 2213 | php, php-cli, composer |
| vde-python | python, python3, py | Python | vde-python | 2214 | python3, python3-pip |
| vde-ruby | ruby | Ruby | vde-ruby | 2215 | ruby-full |
| vde-rust | rust, rs, rustc | Rust | vde-rust | 2216 | rustup |
| vde-scala | scala | Scala | vde-scala | 2217 | scala-defaults, sbt |
| vde-swift | swift | Swift | vde-swift | 2218 | binutils, git, libc6-dev, curl |
| vde-testport1 | testport1 | Test Port 1 | vde-testport1 | 2219 | test |
| vde-testport2 | testport2 | Test Port 2 | vde-testport2 | 2220 | test |

---

## Service VMs (7 total, ports 2400-2499)

| Name | Aliases | Display Name | Container Name | Service Port | SSH Port | Purpose |
|------|---------|--------------|----------------|--------------|----------|---------|
| vde-couchdb | couchdb | CouchDB | vde-couchdb | 5984 | 2400 | NoSQL database |
| vde-mongodb | mongo | MongoDB | vde-mongodb | 27017 | 2401 | Document database |
| vde-mysql | mysql | MySQL | vde-mysql | 3306 | 2402 | MySQL database |
| vde-nginx | nginx | Nginx | vde-nginx | 80, 443 | 2403 | Web server |
| vde-postgres | postgresql | PostgreSQL | vde-postgres | 5432 | 2404 | PostgreSQL database |
| vde-rabbitmq | rabbitmq | RabbitMQ | vde-rabbitmq | 5672, 15672 | 2405 | Message queue |
| vde-redis | redis | Redis | vde-redis | 6379 | 2406 | Key-value store |

---

## Viewing Available VMs

```bash
# List all VMs (using unified CLI)
vde list

# List only language VMs
vde list --lang
# OR
./bin/list-vms --lang

# List only service VMs
vde list --svc
# OR
./bin/list-vms --svc

# Search for specific VMs
vde list python
vde list --lang script
```

---

## Adding New VM Types

See [Extending VDE](./extending-vde.md) for instructions on adding new languages or services.

---

[← Back to README](../README.md)
