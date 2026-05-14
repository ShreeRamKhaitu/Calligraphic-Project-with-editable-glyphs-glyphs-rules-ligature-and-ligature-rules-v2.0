# Running the Calligraphic Project

Follow these steps to get the project up and running:

## 1. Start the Backend Server
Open your terminal in the project directory and run:
```bash
./.venv/bin/python3 api.py
```

## 2. Access the Web UI
Open your browser and navigate to:
**http://localhost:8000**

## 3. Key Features
- **Glyph Studio**: Customize character scaling, offsets, and surgical cropping.
- **Monogram Generator**: Generate vertical stacks with automatic positional rules (First, Middle, Last).
- **Word Builder**: Build words by drawing characters and render them vertically.

## Troubleshooting
- **Address already in use**: If you see an error about port 8000, run `fuser -k 8000/tcp` to clear the port before starting.
- **Missing Dependencies**: All required packages are pre-installed in the `.venv` directory.
