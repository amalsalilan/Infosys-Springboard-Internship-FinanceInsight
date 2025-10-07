import json
from bs4 import BeautifulSoup

def get_highlight_color(sentiment_class, scores):
    """Get color based on sentiment and confidence score."""
    if sentiment_class == 'neutral':
        return None  # Skip neutral sentences

    if sentiment_class == 'positive':
        # Green intensity based on confidence score (0.0 to 1.0)
        # Higher confidence = darker green (lower R and B values)
        base_lightness = 255 - int(scores['positive'] * 155)  # Range: 255 to 100
        return f'rgb({base_lightness}, 255, {base_lightness})'

    elif sentiment_class == 'negative':
        # Red intensity based on confidence score
        # Higher confidence = darker red (lower G and B values)
        base_lightness = 255 - int(scores['negative'] * 155)  # Range: 255 to 100
        return f'rgb(255, {base_lightness}, {base_lightness})'

    return None

def main():
    # Read sentiment analysis results
    with open('output/sentiment_analysis_results.json', 'r', encoding='utf-8') as f:
        sentiments = json.load(f)

    # Read HTML file
    with open('output/company_paragraphs_sample.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # Get all text from body
    body = soup.find('body')
    if not body:
        body = soup

    body_text = body.get_text()

    # Sort sentiments by position (start) in reverse to avoid position shifts
    sentiments_sorted = sorted(sentiments, key=lambda x: x['position']['start'], reverse=True)

    # Apply highlights
    html_str = str(soup)

    for sentiment in sentiments_sorted:
        color = get_highlight_color(sentiment['class'], sentiment['confidence_scores'])

        if color:  # Skip neutral
            sentence = sentiment['sentence']
            # Create highlighted version
            highlighted = f'<span style="background-color: {color};">{sentence}</span>'

            # Replace in HTML
            html_str = html_str.replace(sentence, highlighted, 1)

    # Save to new file
    output_file = 'output/company_paragraphs_highlighted.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_str)

    print(f"Highlighted HTML saved to: {output_file}")
    print(f"- Green highlighting: Positive sentiment (darker = higher confidence)")
    print(f"- Red highlighting: Negative sentiment (darker = higher confidence)")
    print(f"- No highlighting: Neutral sentiment")

if __name__ == "__main__":
    main()
