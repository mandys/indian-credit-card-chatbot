#!/usr/bin/env python3
"""
Automated Test Runner for Credit Card Chatbot
Runs test cases and updates the HTML test file with results
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Tuple
from utils.qa_engine import RichDataCreditCardBot

class TestRunner:
    def __init__(self):
        self.bot = RichDataCreditCardBot(data_files=['data/axis-atlas.json', 'data/icici-epm.json'])
        self.test_cases = self._load_test_cases()
        self.results = []
        
    def _load_test_cases(self) -> List[Dict]:
        """Load test cases from configuration"""
        return [
            {
                "category": "Hotel & Travel Spending",
                "query": "I have a 200,000 hotel spend coming up. Which card is better axis atlas or icici epm?",
                "expected_keywords": ["10,000", "6,000", "atlas", "winner", "travel", "5 EDGE Miles"],
                "expected_winner": "axis atlas"
            },
            {
                "category": "Hotel & Travel Spending", 
                "query": "Which card is better for direct airline bookings?",
                "expected_keywords": ["5 EDGE Miles", "₹100", "travel", "axis atlas"],
                "expected_winner": "axis atlas"
            },
            {
                "category": "Utility Spending",
                "query": "What are the utility charges on ICICI EPM?",
                "expected_keywords": ["1%", "₹50,000", "utility", "fee"],
                "expected_content": "fees and rewards eligibility"
            },
            {
                "category": "Utility Spending",
                "query": "Can I pay utility bills with these cards?",
                "expected_keywords": ["₹50,000", "₹25,000", "1%", "fee", "rewards"],
                "expected_content": "both cards with fees"
            },
            {
                "category": "Reward Comparison",
                "query": "If I spend 100000 which card gives me more rewards?",
                "expected_keywords": ["3,000", "2,000", "ICICI", "winner"],
                "expected_winner": "icici"
            },
            {
                "category": "Miles Transfer",
                "query": "Can I transfer ICICI points to airlines?",
                "expected_keywords": ["iShop platform", "100%", "₹1 per Reward Point", "iMobile application", "flight bookings"],
                "expected_content": "explains ICICI flight redemption through iShop with full payment capability"
            },
            {
                "category": "Fees & Charges",
                "query": "What are the joining fees for both cards?",
                "expected_keywords": ["₹5,000", "₹12,499", "Atlas", "ICICI"],
                "expected_content": "both joining fees"
            },
            {
                "category": "Lounge Access",
                "query": "How many lounge visits do I get with Axis Atlas?",
                "expected_keywords": ["tier", "Silver", "Gold", "Platinum", "domestic", "international"],
                "expected_content": "tier-based lounge access"
            },
            {
                "category": "Insurance Spending",
                "query": "do we get points on insurance payments done using icici epm",
                "expected_keywords": ["6 ICICI Bank Reward Points", "₹200", "5,000", "cap", "insurance"],
                "expected_content": "rewards with cap"
            },
            {
                "category": "Insurance Spending",
                "query": "do we get points on insurance payments done using axis atlas",
                "expected_keywords": ["not", "excluded", "insurance", "no rewards"],
                "expected_content": "excluded from rewards"
            },
            {
                "category": "Insurance Spending",
                "query": "do we get points on insurance payments done by axis atlas or icici epm",
                "expected_keywords": ["ICICI", "5,000", "cap", "axis", "not", "excluded"],
                "expected_content": "comparison showing ICICI yes, Axis no"
            },
            {
                "category": "Government Spending",
                "query": "can we make tax payments using icici epm",
                "expected_keywords": ["excluded", "tax payments", "not earn any rewards", "excluded from earning rewards"],
                "expected_content": "excluded from rewards"
            },
            {
                "category": "Government Spending", 
                "query": "can we make tax payments using axis atlas",
                "expected_keywords": ["excluded", "Government Institution", "do not earn rewards", "tax payments"],
                "expected_content": "excluded from rewards"
            },
            {
                "category": "Government Spending",
                "query": "do we get points on government payments using icici epm and axis atlas",
                "expected_keywords": ["excluded", "no rewards", "Government Institution", "government services"],
                "expected_content": "both cards exclude government payments"
            },
            {
                "category": "Education Spending",
                "query": "Compare both cards for education spends",
                "expected_keywords": ["6 points per ₹200", "2 EDGE Miles per ₹100", "1,000", "cap", "education"],
                "expected_content": "comparison of both cards for education"
            },
            {
                "category": "Education Spending",
                "query": "I have ₹30,000 education fees to pay. Which card is better?",
                "expected_keywords": ["900", "600", "ICICI", "better", "₹30,000"],
                "expected_winner": "icici"
            },
            {
                "category": "Education Spending", 
                "query": "I have ₹1,00,000 education fees to pay. Which card is better?",
                "expected_keywords": ["2,000", "1,000", "cap", "Axis", "better"],
                "expected_winner": "axis"
            },
            {
                "category": "Education Spending",
                "query": "Is education excluded from earning rewards on Axis Atlas?",
                "expected_keywords": ["not excluded", "earns rewards", "2 EDGE Miles", "₹100", "education"],
                "expected_content": "education not excluded, earns rewards"
            },
            # New test cases for recent bug fixes
            {
                "category": "Insurance Benefits",
                "query": "which card has better lost card liability ? axis or icici ?",
                "expected_keywords": ["₹3L", "₹50,000", "Axis", "better", "liability"],
                "expected_winner": "axis",
                "expected_content": "compare card liability coverage amounts"
            },
            {
                "category": "Insurance Benefits", 
                "query": "What insurance benefits does ICICI EPM offer?",
                "expected_keywords": ["₹50,000", "card liability", "₹3,00,00,000", "accident", "insurance"],
                "expected_content": "comprehensive insurance coverage details"
            },
            {
                "category": "Government Spending Comparison",
                "query": "which card is better for government spends?",
                "expected_keywords": ["neither", "excluded", "government", "no rewards"],
                "expected_content": "both cards exclude government spending"
            }
        ]
    
    def run_test(self, test_case: Dict) -> Dict:
        """Run a single test case and return results"""
        query = test_case["query"]
        expected_keywords = test_case.get("expected_keywords", [])
        expected_winner = test_case.get("expected_winner", "")
        expected_content = test_case.get("expected_content", "")
        
        print(f"Testing: {query[:50]}...")
        
        try:
            # Get bot response
            response = self.bot.get_answer(query)
            response_lower = response.lower()
            
            # Check keywords
            keyword_matches = []
            for keyword in expected_keywords:
                if keyword.lower() in response_lower:
                    keyword_matches.append(keyword)
            
            # Check winner (if applicable)
            winner_correct = True
            if expected_winner:
                if expected_winner.lower() not in response_lower:
                    winner_correct = False
            
            # Calculate score
            keyword_score = len(keyword_matches) / len(expected_keywords) if expected_keywords else 1.0
            content_score = 1.0 if not expected_content else (0.8 if any(word in response_lower for word in expected_content.split()) else 0.0)
            winner_score = 1.0 if winner_correct else 0.0
            
            overall_score = (keyword_score * 0.5 + content_score * 0.3 + winner_score * 0.2)
            
            # Determine status
            if overall_score >= 0.8:
                status = "PASSING"
            elif overall_score >= 0.5:
                status = "PARTIAL"
            else:
                status = "FAILING"
            
            return {
                "query": query,
                "category": test_case["category"],
                "response": response,
                "status": status,
                "score": overall_score,
                "keyword_matches": keyword_matches,
                "missing_keywords": [k for k in expected_keywords if k not in keyword_matches],
                "winner_correct": winner_correct,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "query": query,
                "category": test_case["category"],
                "response": f"ERROR: {str(e)}",
                "status": "ERROR",
                "score": 0.0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def run_all_tests(self) -> List[Dict]:
        """Run all test cases"""
        print("🚀 Starting automated test run...")
        print("=" * 60)
        
        results = []
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\n[{i}/{len(self.test_cases)}] {test_case['category']}")
            result = self.run_test(test_case)
            results.append(result)
            
            # Print quick status
            status_emoji = {"PASSING": "✅", "PARTIAL": "⚠️", "FAILING": "❌", "ERROR": "💥"}
            print(f"   {status_emoji.get(result['status'], '❓')} {result['status']} (Score: {result['score']:.2f})")
            
        self.results = results
        return results
    
    def generate_report(self) -> str:
        """Generate a detailed text report"""
        if not self.results:
            return "No test results available. Run tests first."
        
        report = []
        report.append("=" * 80)
        report.append("🧪 CREDIT CARD CHATBOT TEST REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Tests: {len(self.results)}")
        
        # Summary stats
        passing = len([r for r in self.results if r['status'] == 'PASSING'])
        partial = len([r for r in self.results if r['status'] == 'PARTIAL'])
        failing = len([r for r in self.results if r['status'] == 'FAILING'])
        errors = len([r for r in self.results if r['status'] == 'ERROR'])
        
        report.append(f"✅ Passing: {passing}")
        report.append(f"⚠️  Partial: {partial}")
        report.append(f"❌ Failing: {failing}")
        report.append(f"💥 Errors: {errors}")
        report.append(f"📊 Overall Score: {sum(r['score'] for r in self.results) / len(self.results):.1%}")
        report.append("")
        
        # Detailed results
        current_category = None
        for result in self.results:
            if result['category'] != current_category:
                report.append(f"\n📁 {result['category']}")
                report.append("-" * 60)
                current_category = result['category']
            
            status_emoji = {"PASSING": "✅", "PARTIAL": "⚠️", "FAILING": "❌", "ERROR": "💥"}
            report.append(f"\n{status_emoji.get(result['status'], '❓')} {result['status']} (Score: {result['score']:.2f})")
            report.append(f"Query: {result['query']}")
            
            if result.get('missing_keywords'):
                report.append(f"Missing Keywords: {', '.join(result['missing_keywords'])}")
            
            if result['status'] in ['FAILING', 'ERROR']:
                report.append(f"Response: {result['response'][:200]}...")
            
            report.append("")
        
        return "\n".join(report)
    
    def update_html_file(self, html_file: str = "test_cases.html"):
        """Update the HTML test cases file with current results"""
        if not self.results:
            print("No results to update HTML with.")
            return
        
        # Read current HTML
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
        except FileNotFoundError:
            print(f"HTML file {html_file} not found.")
            return
        
        # Update status classes based on results
        for result in self.results:
            query = result['query']
            status = result['status']
            
            # Map status to CSS class
            css_class = {
                'PASSING': 'pass',
                'PARTIAL': 'pending', 
                'FAILING': 'fail',
                'ERROR': 'fail'
            }.get(status, 'pending')
            
            # Find and replace the status cell for this query
            # This is a simple approach - in production you'd want more robust HTML parsing
            query_pattern = re.escape(query[:30])  # Use first 30 chars to match
            status_pattern = rf'({query_pattern}.*?)<td class="(pass|fail|pending)">(PASSING|FAILING|PENDING|ERROR)</td>'
            replacement = rf'\1<td class="{css_class}">{status}</td>'
            
            html_content = re.sub(status_pattern, replacement, html_content, flags=re.DOTALL)
        
        # Add timestamp
        timestamp_html = f'<p class="note">Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>'
        html_content = html_content.replace('</body>', f'{timestamp_html}\n</body>')
        
        # Write updated HTML
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Updated {html_file} with test results")

def main():
    """Main function to run tests"""
    runner = TestRunner()
    
    # Run all tests
    results = runner.run_all_tests()
    
    # Generate and save report
    report = runner.generate_report()
    with open(f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", 'w') as f:
        f.write(report)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passing = len([r for r in results if r['status'] == 'PASSING'])
    total = len(results)
    print(f"✅ {passing}/{total} tests passing ({passing/total:.1%})")
    
    failing_tests = [r for r in results if r['status'] in ['FAILING', 'ERROR']]
    if failing_tests:
        print(f"\n❌ Failed tests:")
        for test in failing_tests:
            print(f"   • {test['query'][:50]}...")
    
    # Update HTML file
    runner.update_html_file()
    
    print(f"\n📄 Detailed report saved to: test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    print(f"🌐 Updated HTML file: test_cases.html")

if __name__ == "__main__":
    main() 