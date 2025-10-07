import requests
import sys

# Test the document converter API
def test_convert():
    url = "http://localhost:8000/convert"

    # Check if file path provided
    if len(sys.argv) < 2:
        print("Usage: python test_api.py <path_to_file>")
        print("Example: python test_api.py sample.pdf")
        return

    file_path = sys.argv[1]

    print(f"Testing API with file: {file_path}")
    print("Uploading...")

    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files, timeout=120)

        print(f"\nStatus Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ SUCCESS!")
            print(f"Filename: {data['filename']}")
            print(f"Format: {data['format']}")
            print(f"Text Length: {len(data['text'])} chars")
            print(f"Markdown Length: {len(data['markdown'])} chars")
            print(f"\nFirst 200 chars of text:")
            print(data['text'][:200])
        else:
            print(f"\n❌ ERROR: {response.text}")

    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
    except requests.exceptions.Timeout:
        print("❌ Request timed out (>120s)")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_convert()
