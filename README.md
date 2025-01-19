# Maktabkhooneh Crawler

Maktabkhooneh Crawler is a command-line tool for interacting with the Maktabkhooneh platform. It allows you to log in, crawl course information, and download course videos.

## Features

- **Login**: Log in to Maktabkhooneh and save cookies for future requests.
- **Crawl Course**: Fetch and save course information based on the course URL.
- **Download Videos**: Download course videos using the information from a JSON file.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/maktabkhooneh-crawler.git
    cd maktabkhooneh-crawler
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. Set up your environment variables:
    - Copy

.env.sample

 to

.env

 and fill in your Maktabkhooneh username and password.

## Usage

### Login

Log in to Maktabkhooneh and save cookies for future requests.

```sh
python main.py login --save-cookies --output "path/to/output"
```

### Crawl Course

Fetch and save course information based on the course URL.

```sh
python main.py crawl-course --course-url "YOUR_COURSE_URL" --output "path/to/output"
```

### Download Videos

Download course videos using the information from a JSON file.

```sh
python main.py download-videos --input-file "path/to/course_info.json" --max-threads 5 --output "path/to/output"
```

## Project Structure

```
maktabkhooneh-crawler/
├── .env
├── .gitignore
├── app.log
├── LICENSE
├── main.py
├── pyproject.toml
├── README.md
├── src/
│   ├── __init__.py
│   ├── _core/
│   │   ├── __init__.py
│   │   ├── logging.py
│   │   ├── schemas.py
│   │   ├── utils.py
│   ├── handler.py
├── temp/
├── tests/
│   ├── test_handler.py
├── uv.lock
```

## License

This project is licensed under the MIT License. See the

LICENSE

 file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes.

## Contact

For any questions or issues, please open an issue on GitHub.
