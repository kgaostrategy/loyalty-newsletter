import os
import requests
from datetime import datetime, timedelta
from openai import OpenAI

NEWS_API_KEY = os.environ['NEWS_API_KEY']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

client = OpenAI(api_key=OPENAI_API_KEY)

def fetch_articles():
 queries = [
 "loyalty program rewards",
 "hotel loyalty rewards",
 "airline miles loyalty",
 "restaurant rewards program",
 "fintech loyalty program",
 "MGM Resorts loyalty",
 "Hard Rock loyalty"
 ]
 
 articles = []
 from_date = (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d')
 
 for query in queries:
 params = {
 "q": query,
 "from": from_date,
 "language": "en",
 "pageSize": 5,
 "sortBy": "relevancy",
 "apiKey": NEWS_API_KEY
 }
 response = requests.get("https://newsapi.org/v2/everything", params=params)
 data = response.json()
 if data.get("articles"):
 articles.extend(data["articles"][:3])
 
 seen = set()
 unique = []
 for a in articles:
 if a['title'] not in seen and a['title'] != '[Removed]':
 seen.add(a['title'])
 unique.append(a)
 
 return unique[:25]

def generate_newsletter(articles):
 today = datetime.today().strftime("%B %d, %Y")
 
 article_text = ""
 for a in articles:
 article_text += f"Title: {a['title']}\nSource: {a['source']['name']}\nURL: {a['url']}\nPublished: {a['publishedAt'][:10]}\nDescription: {a.get('description', 'N/A')}\n\n"
 
 prompt = f"""Today is {today}. You are a senior loyalty industry analyst writing a weekly intelligence briefing.

Here are this week's real news articles to use:

{article_text}

Generate a complete HTML page for a weekly loyalty industry newsletter. Use this exact style:
- Background: #0a0a0a (near black)
- Text: #ffffff
- Accent color: #e63946 (red)
- Font: use Google Fonts - import "Playfair Display" for headings, "Inter" for body
- Premium, editorial, dark financial-briefing aesthetic

Include these sections:
1. Header with issue date ({today}) and title "Loyalty Intelligence Briefing"
2. Executive Summary — 4-5 bullet points of the biggest stories, each with hyperlink and date
3. Industry Themes — 3-4 thematic insights with hyperlinks
4. Competitor Watch — MGM Resorts vs. Hard Rock framing where relevant, plus other competitor moves
5. Footer

STRICT RULES:
- Only use articles provided above — do NOT invent or fabricate any articles
- Every story MUST have a clickable hyperlink to the real URL
- Every story MUST show the published date
- Issue date in header must be {today}
- Output ONLY the raw HTML, no markdown, no explanation"""

 response = client.chat.completions.create(
 model="gpt-4o",
 messages=[{"role": "user", "content": prompt}],
 max_tokens=4000
 )
 
 return response.choices​⟦CITE:0⟧​.message.content.replace("```html", "").replace("```", "").strip()

def save(html):
 today = datetime.today()
 slug = today.strftime("%b%d-%Y").lower()
 
 with open(f"{slug}.html", "w") as f:
 f.write(html)
 
 with open("index.html", "w") as f:
 f.write(html)
 
 print(f"Saved {slug}.html and index.html")

if __name__ == "__main__":
 print("Fetching articles...")
 articles = fetch_articles()
 print(f"Got {len(articles)} articles")
 print("Generating newsletter...")
 html = generate_newsletter(articles)
 save(html)
 print("Done!")
