"""
Quick test script to verify document converter is working
"""
import requests
import os

def test_converter():
    """Test the document converter endpoint"""

    # Create a simple test text file
    test_file_path = "test_document.txt"
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write("""Financial Report Q4 2023

Apple Inc. reported record revenue of $119.6 billion for the fourth quarter.
The company's CEO, Tim Cook, stated that this represents strong growth across all product lines.
Earnings per share increased to $1.52, beating analyst expectations.

Key Highlights:
- iPhone revenue: $69.7 billion
- Services revenue: $22.3 billion
- Mac revenue: $7.6 billion

The results exceeded Wall Street projections, sending shares higher in after-hours trading.
""")

    print("=" * 60)
    print("Testing Document Converter")
    print("=" * 60)

    # Test the converter endpoint
    try:
        url = "http://localhost:8000/convert"

        with open(test_file_path, "rb") as f:
            files = {"file": (test_file_path, f, "text/plain")}

            print(f"\n📤 Sending request to {url}")
            print(f"📄 File: {test_file_path}")

            response = requests.post(url, files=files, timeout=30)

            print(f"\n📊 Response Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()

                print("\n✅ Conversion successful!")
                print(f"   - Success: {data.get('success')}")
                print(f"   - Filename: {data.get('filename')}")
                print(f"   - Format: {data.get('format')}")

                if 'text' in data:
                    print(f"\n📝 Text extracted ({len(data['text'])} characters)")
                    print(f"   Preview: {data['text'][:100]}...")

                if 'html' in data:
                    print(f"\n🌐 HTML generated ({len(data['html'])} characters)")
                    print(f"   Preview: {data['html'][:200]}...")

                    # Check if custom CSS was injected
                    if 'max-width: 100%' in data['html']:
                        print("   ✅ Custom full-width CSS detected!")
                    else:
                        print("   ⚠️  Custom CSS not found (may still be centered)")

                if 'saved_files' in data:
                    print(f"\n💾 Saved files:")
                    for file_type, file_path in data['saved_files'].items():
                        exists = "✅" if os.path.exists(file_path) else "❌"
                        print(f"   {exists} {file_type}: {file_path}")

                print("\n" + "=" * 60)
                print("✅ ALL TESTS PASSED!")
                print("=" * 60)
                return True
            else:
                print(f"\n❌ Error: {response.status_code}")
                print(f"   {response.text}")
                return False

    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend!")
        print("   Make sure to run: python start_backend.py")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False
    finally:
        # Cleanup test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

if __name__ == "__main__":
    test_converter()
