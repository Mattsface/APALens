# APALens

A Flask web application for viewing APA (American Poolplayers Association) team and player statistics.

![Pool APA](https://greaterseattle.apaleagues.com/Uploads/greaterseattle/YO.jpg)

## 🚧 Work in Progress

## Quick Start

```bash
# Install and run
pip install -e .
export APA_REFRESH_TOKEN="your-apa-refresh-token"
export APA_ACCESS_TOKEN="your-apa-access-token"
python -m flask run

# Or with Docker
docker build -t apalens .
docker run -p 5000:5000 \
  -e APA_REFRESH_TOKEN=your-apa-refresh-token \
  -e APA_ACCESS_TOKEN=your-apa-access-token \
  apalens
```

## Contributing
Contributions welcome! Please ensure all tests pass before submitting a PR.

---

**Note**: This application is not affiliated with the American Poolplayers Association (APA). It's an independent tool for viewing publicly available APA statistics.
