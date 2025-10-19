**gRPC + REST Gateway Microservices Example**

This project demonstrates a microservices architecture with gRPC internal communication and a REST API gateway, implemented in Python. This README explains the architecture, generated files, and key concepts for anyone reading or contributing.

1. Architecture Overview

We have two main services in this example:
- UserService
  - Only accepts gRPC requests.
  - Responsible for storing and retrieving user data.

- REST API Gateway
  - Accepts JSON/REST requests from any frontend client.
  - Converts REST requests into gRPC calls to UserService.

Flow:
[Frontend / curl] → REST JSON → [Gateway] → gRPC Stub → [UserService]


2. Why gRPC and REST Together
- REST is widely supported, simple, and suitable for public-facing APIs.
- gRPC is faster for internal microservice communication, thanks to:
    - Binary serialization (Protobuf) → smaller payloads, faster parsing
    - HTTP/2 → multiplexed connections, lower latency, streaming support

We expose REST externally for frontend clients and use gRPC internally for efficiency.

3. Proto file
Key concepts:
- syntax = "proto3"; → use Protobuf version 3
- package user; → defines the namespace, used to avoid name collisions
- service UserService → defines the RPC methods
- message → defines the data structures that will be serialized


4. Generated Python Files

After running:

*python -m grpc_tools.protoc -I protos --python_out=. --grpc_python_out=. protos/user.proto*

We get two files:

4.1 user_pb2.py
- Contains Protobuf message classes only (CreateUserRequest, GetUserResponse, etc.)

- Handles serialization/deserialization to binary Protobuf.

- Both client and server import this file to work with messages.

4.2 user_pb2_grpc.py
- Contains gRPC service classes:

    - UserServiceServicer → server base class

    -  UserServiceStub → client stub

    - Optional UserService → experimental static API

| Name                         | Role              | Used by                            |
| ---------------------------- | ----------------- | ---------------------------------- |
| `UserServiceServicer`        | Server base class | Server implements methods          |
| `UserServiceStub`            | Client stub       | REST gateway or other microservice |
| `UserService` (experimental) | Optional helper   | Rarely used                        |

The convention is: <ServiceName>Servicer and <ServiceName>Stub in Python.
- add_UserServiceServicer_to_server(servicer, server) → registers your server implementation with gRPC.
    - Pattern: add_<ServiceName>Servicer_to_server

5. Working Across Repositories

Generated classes are convenient, but the true contract is the .proto file.

If the client and server are in different repos:

- Share the .proto file and generate Python code in each repo or

- Package the generated files as a library for client consumption

This ensures client and server stay compatible without needing to share the full server code.

6. REST to gRPC Converter

6.1 What is a gRPC Channel?

A channel in gRPC is basically a virtual connection between a client (your REST gateway) and a gRPC server (your UserService).

Think of it as a “pipe” that:

- Knows the address and port of the server (localhost:50051 here),
- Manages HTTP/2 connections under the hood,
- Handles serialization/deserialization of protobuf messages,
- Takes care of connection pooling, timeouts, retries, and load balancing (if configured).

So this line: "channel = grpc.insecure_channel("localhost:50051")" creates a client-side communication channel over HTTP/2 to your running gRPC server.

6.2 What does the stub do?
The stub is an auto-generated client for your gRPC service.
It uses the channel you created to send actual RPC requests to the server.

For example, this line: "grpc_response = stub.CreateUser(grpc_request)" does the following:
- The stub serializes your Python object (grpc_request) into bytes (protobuf format).
- Sends it over the channel via HTTP/2 to the server.
- Waits for the response from the server.
- Deserializes the response bytes into a Python object (grpc_response).


**How the code is structured**
REST_gRPC_Converter/
│
├── protos/
│   └── user.proto                  # Schema definition
│
├── user_server.py                  # gRPC server (UserService)
├── rest_gateway.py                 # REST → gRPC converter (FastAPI)
│
├── user_pb2.py                     # Generated protobuf message classes
├── user_pb2_grpc.py                # Generated gRPC client/server classes
│
└── README.md



**How to run this code**
Run the gRPC server in Terminal 1:
python user_service.py

Run the REST gateway in Terminal 2:
uvicorn rest_gateway:app --reload --port 8000

Test with curl commands:
Create a user using the following:
curl -X POST http://localhost:8000/users \
-H "Content-Type: application/json" \
-d '{"id":"1","name":"Alice","email":"alice@example.com"}'

Get the same user using the following:
curl http://localhost:8000/users/1

