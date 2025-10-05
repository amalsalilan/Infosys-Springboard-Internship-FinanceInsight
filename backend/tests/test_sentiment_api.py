import requests
import json

# Read test data
with open('output/company_paragraphs_sample.txt', 'r', encoding='utf-8') as f:
    text_content = f.read()

with open('output/company_paragraphs_sample.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Test the API
print("Testing Sentiment Analysis API...")
print("=" * 50)

# Call the API
response = requests.post(
    'http://localhost:8001/analyze',
    json={
        'text': text_content,
        'html': html_content
    }
)

if response.status_code == 200:
    result = response.json()

    print(f"\nAPI call successful!")
    print(f"\nFound {len(result['sentiment_results'])} sentences\n")

    # Display results
    for i, sentiment in enumerate(result['sentiment_results'], 1):
        print(f"Sentence {i}:")
        print(f"  Text: {sentiment['sentence'][:80]}...")
        print(f"  Class: {sentiment['class']}")
        print(f"  Position: {sentiment['position']}")
        print(f"  Confidence: Pos={sentiment['confidence_scores']['positive']:.3f}, "
              f"Neg={sentiment['confidence_scores']['negative']:.3f}, "
              f"Neu={sentiment['confidence_scores']['neutral']:.3f}")
        print()

    # Save highlighted HTML
    if result['highlighted_html']:
        output_file = 'output/test_highlighted_output.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result['highlighted_html'])
        print(f"Highlighted HTML saved to: {output_file}")

    # Save JSON results
    json_output = 'output/test_sentiment_results.json'
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(result['sentiment_results'], f, indent=2)
    print(f"JSON results saved to: {json_output}")

else:
    print(f"API call failed with status {response.status_code}")
    print(f"Error: {response.text}")
