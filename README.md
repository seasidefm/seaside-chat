# Seaside Chat

Seaside Chat is a microservice designed to handle chat functionality within the larger SeasideFM livestream platform ecosystem. This service allows users to engage in real-time communication, enhancing the overall user experience during livestreams.

## Features

- **Usernames with Colors:** Each user is assigned a unique and colorful username, making it easy to distinguish participants in the chat.

- **Logging:** Comprehensive logging with color-coded outputs for different log levels, providing easy monitoring and issue identification.

- **Microservice Architecture:** Seaside Chat is designed as a microservice, allowing for scalability and modular integration within the SeasideFM platform.

## Getting Started

### Prerequisites

- Python 3.x
- Dependencies: Install dependencies using the provided `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### Configuration

1. **Log Configuration:**
   - Modify the logging configuration in the `setup_logger` function in `app.py` to suit your preferences.

2. **Username Colors:**
   - Adjust the `usernameColors` object in `app.py` to customize the colors assigned to usernames.

### Usage

Run the Seaside Chat application:

```bash
python main.py
```

The chat service will be accessible at `http://localhost:8000`.

## Logging

Logs are generated in both a rotating file (`app.log`) and displayed in the console. Color-coded log messages provide insights into the application's behavior.

## Contributing

We welcome contributions to enhance the functionality and features of Seaside Chat. Feel free to fork the repository, make your changes, and submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- Seaside Chat is part of the SeasideFM livestream platform ecosystem.
