# AI Chat Assistant

A modern, simple chat UI powered by Flask, HTMX, and OpenAI Agent SDK that enables search and question-answering capabilities.

## Features

- Web search capabilities
- Simple, modern chat interface
- Real-time response handling with HTMX
- Docker support for easy setup

## Setup

### Prerequisites

- Docker and Docker Compose
- OpenAI API key

### Installation

1. Clone this repository
2. Set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

3. Build and start the application:

```bash
docker-compose up --build
```

The application will be available at http://localhost:5001

## Usage

Simply open the application in your browser, type a question in the chat input, and press Send. The AI assistant will search the web for information and respond to your question.

## Development

To make changes to the application:

1. Modify the code as needed
2. Restart the Docker container:

```bash
docker-compose restart
```

For hot-reloading during development, Flask's debug mode is enabled by default.

## Technologies Used

- Flask
- HTMX
- OpenAI Agent SDK
- Docker
