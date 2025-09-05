import openai
import os
import json
import re
from collections import Counter
from typing import Dict, List, Any
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        self.use_mock = True
        
        if self.api_key and self.api_key != "your_openai_api_key_here" and self.api_key.strip() != "":
            try:
                self.client = openai.OpenAI(api_key=self.api_key)
                self.use_mock = False
                print("✅ OpenAI client initialized successfully")
            except Exception as e:
                print(f"⚠️  OpenAI initialization failed: {e}. Using mock mode.")
                self.client = None
                self.use_mock = True
        else:
            print("ℹ️  No OpenAI API key provided. Using mock mode.")
            
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
    
    def extract_keywords(self, text: str, top_k: int = 3) -> List[str]:
        """Extract the most frequent nouns from the text"""
        try:
            words = word_tokenize(text.lower())
            stop_words = set(stopwords.words('english'))
            
            filtered_words = [
                word for word in words 
                if word.isalpha() and len(word) > 3 and word not in stop_words
            ]
            
            word_freq = Counter(filtered_words)
            return [word for word, _ in word_freq.most_common(top_k)]
        except Exception:
            words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
            return list(set(words))[:top_k]
    
    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text using LLM and extract structured data"""
        if not text.strip():
            raise ValueError("Empty input text")
        
        keywords = self.extract_keywords(text)
        
        if self.use_mock:
            return self._mock_analysis(text, keywords)
        
        try:
            prompt = f"""
            Analyze the following text and provide a JSON response with:
            1. A 1-2 sentence summary
            2. A title (extract from text or generate one)
            3. 3 key topics
            4. Sentiment (positive/neutral/negative)
            
            Text: {text}
            
            Respond only with valid JSON in this format:
            {{
                "summary": "...",
                "title": "...",
                "topics": ["topic1", "topic2", "topic3"],
                "sentiment": "positive|neutral|negative"
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.3
            )
            
            response_content = response.choices[0].message.content.strip()
            
            try:
                result = json.loads(response_content)
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    raise ValueError("No valid JSON found in response")
            
            result = {
                "summary": result.get("summary", "Summary not available"),
                "title": result.get("title", "Analysis Result"),
                "topics": result.get("topics", ["general", "content", "analysis"])[:3],
                "sentiment": result.get("sentiment", "neutral"),
                "keywords": keywords
            }
            
            if result["sentiment"] not in ["positive", "negative", "neutral"]:
                result["sentiment"] = "neutral"
                
            return result
            
        except Exception as e:
            print(f"LLM API failed: {e}")
            return self._mock_analysis(text, keywords)
    
    def _mock_analysis(self, text: str, keywords: List[str]) -> Dict[str, Any]:
        """Mock analysis when LLM is not available - provides intelligent fallback"""
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if len(sentences) >= 2:
            summary = '. '.join(sentences[:2]) + '.'
        elif len(sentences) == 1:
            summary = sentences[0] + '.'
        else:
            summary = text[:150] + ('...' if len(text) > 150 else '')
        
        words = text.split()
        if len(words) > 0:
            capitalized_words = [word for word in words[:20] if word[0].isupper() and len(word) > 2]
            if len(capitalized_words) >= 2:
                title = ' '.join(capitalized_words[:4])
            else:
                title = f"Document Analysis - {len(words)} words"
        else:
            title = "Text Analysis"
        
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'positive', 'success', 
                         'love', 'like', 'enjoy', 'happy', 'satisfied', 'pleased', 'effective', 'efficient', 
                         'outstanding', 'remarkable', 'impressive', 'beneficial', 'advantageous']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'negative', 'failure', 'problem', 'issue',
                         'hate', 'dislike', 'unhappy', 'disappointed', 'frustrated', 'concerned', 'worried',
                         'difficult', 'challenging', 'poor', 'weak', 'insufficient', 'inadequate']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count + 1:
            sentiment = "positive"
        elif neg_count > pos_count + 1:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        topics = []
        if keywords:
            topics.extend(keywords[:2])
        
        text_lower = text.lower()
        topic_indicators = {
            'technology': ['technology', 'computer', 'software', 'digital', 'internet', 'ai', 'artificial', 'intelligence'],
            'business': ['business', 'company', 'market', 'revenue', 'profit', 'customer', 'sales'],
            'science': ['research', 'study', 'data', 'analysis', 'scientific', 'experiment', 'results'],
            'health': ['health', 'medical', 'treatment', 'patient', 'disease', 'medicine', 'doctor'],
            'education': ['education', 'learning', 'student', 'school', 'university', 'teaching', 'knowledge']
        }
        
        for topic, indicators in topic_indicators.items():
            if any(indicator in text_lower for indicator in indicators) and topic not in topics:
                topics.append(topic)
                if len(topics) >= 3:
                    break
        
        while len(topics) < 3:
            generic_topics = ['content', 'information', 'communication', 'analysis', 'discussion']
            for topic in generic_topics:
                if topic not in topics:
                    topics.append(topic)
                    break
        
        return {
            "summary": summary,
            "title": title,
            "topics": topics[:3],
            "sentiment": sentiment,
            "keywords": keywords
        }
